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
            
            if not response.get("items"):
                return None
            
            item = response["items"][0]
            stats = item["statistics"]
            return {
                "subscribers": int(stats.get("subscriberCount", 0)),
                "total_views": int(stats.get("viewCount", 0)),
                "video_count": int(stats.get("videoCount", 0)),
                "title": item["snippet"].get("title"),
                "thumbnail": item["snippet"].get("thumbnails", {}).get("default", {}).get("url")
            }
        except Exception as e:
            logger.error(f"Error fetching channel stats: {e}")
            return None

    def get_video_stats(self, video_id):
        """Fetch statistics (views, etc.) for a specific video ID."""
        try:
            request = self.youtube.videos().list(
                part="statistics,snippet",
                id=video_id
            )
            response = request.execute()
            
            if not response.get("items"):
                return None
            
            item = response["items"][0]
            return {
                "viewCount": item["statistics"].get("viewCount", "0"),
                "likeCount": item["statistics"].get("likeCount", "0"),
                "commentCount": item["statistics"].get("commentCount", "0"),
                "title": item["snippet"].get("title"),
                "publishedAt": item["snippet"].get("publishedAt")
            }
        except Exception as e:
            logger.error(f"Error fetching stats for video {video_id}: {e}")
            return None
