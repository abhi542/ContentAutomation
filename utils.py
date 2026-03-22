import os
import json
import logging
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import config

# Setup logging to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def scan_videos(directory: Path):
    """Scan directory for .mp4 files."""
    return list(directory.glob("*.mp4"))

def extract_keyword(filename: str):
    """
    Extract keyword from filename:
    'why-you-cant-focus.mp4' -> 'why you cant focus'
    """
    cleaned = filename.lower()
    if cleaned.endswith(".mp4"):
        cleaned = cleaned[:-4]
    return cleaned.replace("-", " ").replace("_", " ").strip()

def log_upload(data: dict):
    """Log upload details to a JSON file."""
    log_path = config.LOG_FILE
    logs = []
    
    if log_path.exists():
        try:
            with open(log_path, "r") as f:
                logs = json.load(f)
        except (json.JSONDecodeError, IOError):
            logger.error(f"Failed to read log file {log_path}")

    # Add YouTube URL if video_id is present
    if "video_id" in data and data["video_id"]:
        data["youtube_url"] = f"https://youtu.be/{data['video_id']}"

    logs.append({
        **data,
        "timestamp": datetime.now().isoformat()
    })

    with open(log_path, "w") as f:
        json.dump(logs, f, indent=4)

def move_to_posted(file_path: Path):
    """Move processed file to posted folder."""
    dest = config.POSTED_DIR / file_path.name
    try:
        shutil.move(str(file_path), str(dest))
        logger.info(f"Moved {file_path.name} to {config.POSTED_DIR.name}")
    except Exception as e:
        logger.error(f"Error moving file {file_path}: {e}")

def is_processed(filename: str):
    """Check if file was already logged as successful."""
    if not config.LOG_FILE.exists():
        return False
    
    try:
        with open(config.LOG_FILE, "r") as f:
            logs = json.load(f)
            return any(log.get("filename") == filename and log.get("status") == "success" for log in logs)
    except Exception:
        return False

def get_video_duration(file_path: Path):
    """Get video duration using ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return float(result.stdout)
    except Exception as e:
        logger.error(f"Error getting duration for {file_path.name}: {e}")
        return 0

def check_scheduling_status():
    """
    Check if we can post based on:
    1. Daily limit
    2. Minimum gap since last post
    """
    if not config.LOG_FILE.exists():
        return True, ""
    
    try:
        with open(config.LOG_FILE, "r") as f:
            logs = json.load(f)
            success_logs = [log for log in logs if log.get("status") == "success"]
            
            if not success_logs:
                return True, ""
            
            # Sort by timestamp
            success_logs.sort(key=lambda x: x.get("timestamp"), reverse=True)
            last_post = success_logs[0]
            last_timestamp = datetime.fromisoformat(last_post["timestamp"])
            
            # 1. Check Daily Limit (Last 24h)
            last_24h = [log for log in success_logs if datetime.fromisoformat(log["timestamp"]) > datetime.now() - timedelta(days=1)]
            if len(last_24h) >= config.MAX_POSTS_PER_DAY:
                return False, f"Daily limit of {config.MAX_POSTS_PER_DAY} reached ({len(last_24h)} posted in 24h)."
            
            # 2. Check Gap
            gap_needed = timedelta(hours=config.POSTING_GAP_HOURS)
            if datetime.now() < last_timestamp + gap_needed:
                wait_time = (last_timestamp + gap_needed) - datetime.now()
                return False, f"Gap not met. Next post allowed in {str(wait_time).split('.')[0]}."
                
            return True, ""
    except Exception as e:
        logger.error(f"Error checking scheduling status: {e}")
        return True, ""
