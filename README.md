# ReelsToShorts 🚀

A production-ready Python automation system that syncs Instagram Reels to YouTube Shorts using AI for viral, high-CTR metadata.

## 🎯 Features
- **Instagram Auto-Sync**: Detects and downloads new Reels from any profile.
- **Viral AI Metadata**: Uses 2025-2026 growth strategies to generate curiositiy-driven, high-CTR titles (LLM Powered).
- **Smart Scheduling**: Implements 6-hour gaps and daily post limits to avoid audience saturation.
- **YouTube Shorts API**: Handles secure OAuth2 authentication and resumable uploads.
- **Success Logs**: Generates a JSON history with clickable YouTube links for every post.

---

## 📁 System Structure
- `input_videos/`: Target folder for new content.
- `posted/`: Archive for successfully uploaded videos.
- `logs/`: Check `uploads.json` for activity history.
- `instagram_sync.py`: Handles Reels detection and download.
- `metadata_generator.py`: Generates the hooks and titles.

---

## 🛠 Setup & Installation

### 1. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_key_here
INSTAGRAM_USER=your_username
INSTAGRAM_PROFILE=target_username
POSTING_GAP_HOURS=6
MAX_POSTS_PER_DAY=3
```

### 3. Google Cloud Setup (YouTube API)
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Enable **YouTube Data API v3**.
3. Create **OAuth 2.0 Client ID** (Desktop App).
4. Download the JSON and save it as `client_secrets.json` in the project root.
5. Add your email as a **Test User** in the OAuth Consent Screen.

### 4. Authorize Instagram
To avoid 403 blocks, perform a one-time login:
```bash
instaloader --login YOUR_USERNAME
```

---

## 🚀 Running the Automation

### Continuous Watch Mode (Recommended)
Automatically syncs Reels and uploads them to YouTube every 12 hours:
```bash
python main.py --watch
```

### Manual Trigger
Run a sync and upload session immediately:
```bash
python main.py --run
```

---

## 💡 Important Notes
- **Instagram Blocks**: If you see "401 Unauthorized" or "Please wait," Instagram has rate-limited you. Wait 12-24 hours before retrying.
- **Metadata**: AI generates metadata based on the video filename. Ensure your files or Reels have descriptive names.
