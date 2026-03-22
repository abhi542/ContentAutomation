import os
import json
import logging
import shutil
from datetime import datetime
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
