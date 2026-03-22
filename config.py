import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project Paths
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / os.getenv("INPUT_DIR", "input_videos")
POSTED_DIR = BASE_DIR / os.getenv("POSTED_DIR", "posted")
LOGS_DIR = BASE_DIR / "logs"
LOG_FILE = LOGS_DIR / os.getenv("LOG_FILE", "uploads.json")

# Ensure directories exist
for directory in [INPUT_DIR, POSTED_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# AI Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o") # or "llama3-70b-8192" for Groq

# YouTube Settings
CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRETS_FILE", "client_secrets.json")
YOUTUBE_SCOPE = ["https://www.googleapis.com/auth/youtube.upload"]
CATEGORY_ID = 22 # People & Blogs
PRIVACY_STATUS = "public"
