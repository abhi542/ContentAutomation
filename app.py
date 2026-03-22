import os
import json
import logging
from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime
import config
import main
from utils import scan_videos
from uploader import YouTubeUploader

# Set up logging for the web app
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Dashboard")

app = FastAPI(title="ContentAutomation Dashboard")

# Serve static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def read_index():
    return FileResponse(static_dir / "index.html")

@app.get("/api/stats")
async def get_stats():
    """Return system statistics."""
    total_reels = len(scan_videos(config.INPUT_DIR))
    
    logs = []
    if config.LOG_FILE.exists():
        with open(config.LOG_FILE, "r") as f:
            logs = json.load(f)
            
    success_logs = [l for l in logs if l.get("status") == "success"]
    last_post = success_logs[-1] if success_logs else None
    
    # Calculate next recommended post time
    can_post, reason = main.check_scheduling_status()
    
    # Fetch live stats for the last post if it exists
    live_stats = None
    channel_stats = None
    try:
        uploader = YouTubeUploader()
        channel_stats = uploader.get_channel_stats()
        if last_post and last_post.get("video_id"):
            live_stats = uploader.get_video_stats(last_post["video_id"])
    except:
        pass

    # Extract dynamic countdown if present in reason
    next_post_time_str = "00:00:00"
    if "Next post allowed in" in reason:
        import re
        match = re.search(r"(\d+):(\d+):(\d+)", reason)
        if match:
            h, m, s = match.groups()
            next_post_time_str = f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
    elif "limit" in reason.lower():
        # If daily limit reached, timer should show time until next window (e.g. roughly 12-24h)
        # For simplicity, we'll just indicate "Limit"
        next_post_time_str = "LIMIT"
    
    # Calculate more metrics
    total_views = 0
    if live_stats:
        total_views = int(live_stats.get("viewCount", 0))

    return {
        "videos_queued": total_reels,
        "total_posted": len(success_logs),
        "last_post": last_post,
        "live_stats": live_stats,
        "can_post_now": can_post,
        "scheduling_reason": reason,
        "next_post_timer": next_post_time_str,
        "metrics": {
            "total_views": channel_stats.get("total_views", 0) if channel_stats else 0,
            "subscribers": channel_stats.get("subscribers", 0) if channel_stats else 0,
            "video_count": channel_stats.get("video_count", 0) if channel_stats else 0,
            "total_likes": int(live_stats.get("likeCount", 0)) if live_stats else 0,
            "success_rate": "100%",
            "account_status": "Healthy"
        },
        "channel": channel_stats,
        "config": {
            "gap_hours": config.POSTING_GAP_HOURS,
            "max_daily": config.MAX_POSTS_PER_DAY
        }
    }

    return {
        "videos_queued": total_reels,
        "total_posted": len(success_logs),
        "last_post": last_post,
        "live_stats": live_stats,
        "can_post_now": can_post,
        "scheduling_reason": reason,
        "next_post_timer": next_post_time_str,
        "config": {
            "gap_hours": config.POSTING_GAP_HOURS,
            "max_daily": config.MAX_POSTS_PER_DAY
        }
    }

@app.get("/api/logs")
async def get_logs():
    """Return the last 20 upload logs."""
    if not config.LOG_FILE.exists():
        return []
    with open(config.LOG_FILE, "r") as f:
        logs = json.load(f)
        processed_logs = logs[::-1][:10] # Newest 10 for performance
        
        # Optionally inject video thumbnails
        for log in processed_logs:
            if log.get("video_id"):
                log["thumbnail"] = f"https://img.youtube.com/vi/{log['video_id']}/mqdefault.jpg"
                log["youtube_url"] = f"https://www.youtube.com/shorts/{log['video_id']}"
        
        return processed_logs

@app.post("/api/trigger")
async def trigger_post(background_tasks: BackgroundTasks):
    """Manually trigger a post session (ignoring the gap)."""
    background_tasks.add_task(main.process_videos, force=True)
    return {"message": "Automation triggered in background."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
