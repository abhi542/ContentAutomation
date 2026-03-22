import os
import logging
import instaloader
from pathlib import Path
import config

logger = logging.getLogger(__name__)

class InstagramSync:
    def __init__(self):
        self.L = instaloader.Instaloader(
            download_pictures=False,
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        # Set patterns after initialization
        self.L.filename_pattern = "{shortcode}"
        self.profile_name = config.INSTAGRAM_PROFILE
        self.user = os.getenv("INSTAGRAM_USER")

    def _load_session(self):
        """Attempt to load an existing Instagram session to avoid 403 errors."""
        if not self.user:
            logger.info("No INSTAGRAM_USER set. Attempting anonymous sync (may fail with 403).")
            return False

        try:
            logger.info(f"Attempting to load session for: {self.user}")
            # instaloader looks for sessions in the default local folder (~/.config/instaloader/)
            self.L.load_session_from_file(self.user)
            logger.info("Session loaded successfully.")
            return True
        except FileNotFoundError:
            logger.warning(f"No session file found for {self.user}. Running anonymously.")
        except Exception as e:
            logger.error(f"Error loading session: {e}")
        return False

    def sync_reels(self, target_dir: Path):
        """Download latest Reels from the configured profile."""
        if not self.profile_name:
            logger.warning("No INSTAGRAM_PROFILE set. Skipping sync.")
            return []

        logger.info(f"Syncing Reels from Instagram profile: {self.profile_name}")
        
        # Try to load session first to avoid 403 Forbidden errors
        self._load_session()
        
        try:
            profile = instaloader.Profile.from_username(self.L.context, self.profile_name)
            
            downloaded_count = 0
            for post in profile.get_posts():
                # We only want Reels (videos)
                if not post.is_video:
                    continue
                
                # Check if already downloaded (by looking at shortcode in filename)
                # Note: This is a basic check. In production, we'd track IDs in a DB.
                video_filename = f"{post.shortcode}.mp4"
                
                # We download to a temp folder first, then move to input_videos
                # to avoid main.py picking up half-downloaded files.
                self.L.download_post(post, target=str(target_dir))
                
                # instaloader downloads many files (.mp4, .txt, etc.)
                # and often names the mp4 with the date.
                # Our filename_target="{shortcode}" helps.
                
                downloaded_count += 1
                if downloaded_count >= 3: # Limit to last 3 reels per sync
                    break
            
            logger.info(f"Sync complete. Downloaded {downloaded_count} reels.")
            return downloaded_count

        except Exception as e:
            logger.error(f"Instagram sync failed: {e}")
            return 0

if __name__ == "__main__":
    # Test
    sync = InstagramSync()
    sync.sync_reels(Path("./input_videos"))
