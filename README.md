# ContentAutomation 🚀

A production-ready Python automation system that uploads YouTube Shorts using the YouTube Data API v3 and generates HIGH-CTR metadata using AI.

## 🎯 Features
- **Folder Scanner**: Detects new `.mp4` files and extracts keywords from filenames.
- **AI Metadata Generator**: Uses LLMs (OpenAI/Groq) to generate viral, psychological-trigger-based titles.
- **YouTube Upload**: Handles OAuth2 authentication and resumable uploads.
- **Smart Logging**: Prevents duplicate uploads and logs success/failure in JSON format.
- **Automation Modes**: Support for single runs and 12-hour continuous watching.

## 📁 Project Structure
- `main.py`: Entry point for the automation.
- `uploader.py`: YouTube API integration.
- `metadata_generator.py`: LLM-powered SEO engine.
- `config.py`: Configuration and environment variables management.
- `utils.py`: Logging and file management utilities.

## ⚙️ Setup

### 1. Requirements
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file based on `.env.example`:
```env
GROQ_API_KEY=your_key_here
AI_MODEL=llama-3.3-70b-versatile
```

### 3. YouTube API
- Create a project on [Google Cloud Console](https://console.cloud.google.com/).
- Enable **YouTube Data API v3**.
- Create **OAuth client ID** (Desktop app).
- Download and name it `client_secrets.json` in the root folder.
- Add your email to **Test users** in the OAuth Consent Screen.

## 🛠 Usage

### Run Once
```bash
python main.py --run
```

### Watch Mode (Every 12 Hours)
```bash
python main.py --watch
```
