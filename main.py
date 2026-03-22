import argparse
import time
import schedule
import logging
from pathlib import Path
import config
from utils import scan_videos, extract_keyword, log_upload, move_to_posted, is_processed, get_video_duration, check_scheduling_status
from metadata_generator import MetadataGenerator
from uploader import YouTubeUploader

logger = logging.getLogger(__name__)

def process_videos():
    """Main process to scan, generate metadata, and upload."""
    logger.info("Starting video processing session...")
    
    videos = scan_videos(config.INPUT_DIR)
    if not videos:
        logger.info("No new videos found in input directory.")
        return

    # Check Scheduling Status
    can_post, reason = check_scheduling_status()
    if not can_post:
        logger.info(f"Skipping session: {reason}")
        return

    # Initialize components
    try:
        metadata_gen = MetadataGenerator()
        uploader = YouTubeUploader()
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        return

    posted_this_session = False

    for video_path in videos:
        # Only post ONE per session in watch mode to respect gaps
        if posted_this_session:
            break

        filename = video_path.name
        
        if is_processed(filename):
            logger.info(f"Skipping already processed video: {filename}")
            continue

        # 1. Extract Keyword
        keyword = extract_keyword(filename)
        
        # 2. Generate Metadata
        metadata = metadata_gen.generate(keyword)
        
        # 3. Upload to YouTube
        max_retries = 2
        attempt = 0
        success = False
        video_id = None
        error_msg = ""

        while attempt < max_retries and not success:
            try:
                video_id = uploader.upload_video(
                    video_path,
                    metadata["best_title"],
                    metadata["description"],
                    metadata["tags"]
                )
                success = True
            except Exception as e:
                attempt += 1
                error_msg = str(e)
                logger.error(f"Upload attempt {attempt} failed for {filename}: {e}")
                if attempt < max_retries:
                    time.sleep(10) # Wait before retry

        # 4. Post-Upload Handling
        if success:
            log_upload({
                "filename": filename,
                "title": metadata["best_title"],
                "video_id": video_id,
                "status": "success"
            })
            move_to_posted(video_path)
            logger.info(f"Successfully posted {filename} (ID: {video_id})")
            posted_this_session = True # Respect gap after one post
        else:
            log_upload({
                "filename": filename,
                "status": "failed",
                "error": error_msg
            })
            logger.error(f"Failed to upload {filename} after {max_retries} attempts.")

def main():
    parser = argparse.ArgumentParser(description="YouTube Shorts Automation System")
    parser.add_argument("--run", action="store_true", help="Run once and exit")
    parser.add_argument("--watch", action="store_true", help="Run continuously every 12 hours")
    args = parser.parse_args()

    if args.run:
        process_videos()
    elif args.watch:
        logger.info("Automation started. Watching every 12 hours...")
        process_videos() # Run once immediately
        schedule.every(12).hours.do(process_videos)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
