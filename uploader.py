import os
import pickle
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import config

logger = logging.getLogger(__name__)

class YouTubeUploader:
    def __init__(self):
        self.youtube = self._get_authenticated_service()

    def _get_authenticated_service(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(config.CLIENT_SECRETS_FILE):
                    raise FileNotFoundError(f"Missing {config.CLIENT_SECRETS_FILE}. Please download from Google Cloud Console.")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.CLIENT_SECRETS_FILE, config.YOUTUBE_SCOPE)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build("youtube", "v3", credentials=creds)

    def upload_video(self, file_path, title, description, tags):
        """Upload video to YouTube."""
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": config.CATEGORY_ID
            },
            "status": {
                "privacyStatus": config.PRIVACY_STATUS,
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(
            str(file_path),
            chunksize=-1,
            resumable=True
        )

        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        logger.info(f"Uploading video: {file_path.name}...")
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"Uploaded {int(status.progress() * 100)}%")

        logger.info(f"Upload complete! Video ID: {response.get('id')}")
        return response.get("id")

    def get_channel_stats(self):
        """Fetch overall channel statistics (subscribers, total views)."""
        try:
            request = self.youtube.channels().list(
                part="statistics,snippet",
                mine=True
            )
            response = request.execute()
            logger.info(f"Raw Channel Stats Response: {response}")
            
            if not response.get("items"):
                logger.warning("No channel items found in API response.")
                return None
            
            item = response["items"][0]
            stats = item["statistics"]
            res = {
                "subscribers": int(stats.get("subscriberCount", 0)),
                "total_views": int(stats.get("viewCount", 0)),
                "video_count": int(stats.get("videoCount", 0)),
                "title": item["snippet"].get("title"),
                "thumbnail": item["snippet"].get("thumbnails", {}).get("default", {}).get("url")
            }
            logger.info(f"Processed Channel Stats: {res}")
            return res
        except Exception as e:
            logger.error(f"Error fetching channel stats: {e}")
            return None

    def get_shorts_views_90d(self):
        """Aggregate views for all videos posted in the last 90 days using activities.list."""
        try:
            from datetime import datetime, timedelta, timezone
            since_90d = (datetime.now(timezone.utc) - timedelta(days=90))
            
            # 1. List activities (upload events)
            request = self.youtube.activities().list(
                part="snippet,contentDetails",
                mine=True,
                maxResults=50
            )
            response = request.execute()
            
            video_ids = []
            for item in response.get("items", []):
                if item["snippet"]["type"] == "upload":
                    pub_at = datetime.fromisoformat(item["snippet"]["publishedAt"].replace('Z', '+00:00'))
                    if pub_at > since_90d:
                        v_id = item["contentDetails"]["upload"].get("videoId")
                        if v_id:
                            video_ids.append(v_id)
            
            if not video_ids:
                return 0
            
            # 2. Get stats for these videos
            stats_request = self.youtube.videos().list(
                part="statistics",
                id=",".join(video_ids[:50]) # API limit
            )
            stats_response = stats_request.execute()
            
            total_views = sum(int(item["statistics"].get("viewCount", 0)) for item in stats_response.get("items", []))
            return total_views
        except Exception as e:
            logger.error(f"Error calculating 90d views via activities: {e}")
            return 0

    def get_video_stats(self, video_id):
        """Fetch statistics (views, etc.) for a specific video ID."""
        try:
            request = self.youtube.videos().list(
                part="statistics,snippet",
                id=video_id
            )
            response = request.execute()
            logger.info(f"Raw Video Stats Response for {video_id}: {response}")
            
            if not response.get("items"):
                logger.warning(f"No video items found for ID: {video_id}")
                return None
            
            item = response["items"][0]
            res = {
                "viewCount": item["statistics"].get("viewCount", "0"),
                "likeCount": item["statistics"].get("likeCount", "0"),
                "commentCount": item["statistics"].get("commentCount", "0"),
                "title": item["snippet"].get("title"),
                "publishedAt": item["snippet"].get("publishedAt")
            }
            logger.info(f"Processed Video Stats: {res}")
            return res
        except Exception as e:
            logger.error(f"Error fetching stats for video {video_id}: {e}")
            return None
