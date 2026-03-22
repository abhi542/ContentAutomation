# ⚡ ContentAutomation | PRO-ADMIN EDITION

**The ultimate command center for YouTube Shorts automation. Sync, monitor, and scale your channel with AI-driven precision.**

![Pro-Admin Dashboard Preview](file:///Users/abhinavbhatt/.gemini/antigravity/brain/238f0245-aad4-4dcd-b534-74677ae6a67d/pro_admin_dashboard_final_v2_2_1774170033904.png)

## 💎 The Pro-Admin Advantage
Transform your content pipeline into a professional media house. **ContentAutomation** doesn't just upload videos; it provides real-time business intelligence for your YouTube growth.

### 📊 Advanced Analytics & Monitoring
- **Monetization Tracker**: Live progress bars for **1,000 Subscribers** and **10M Shorts Views** (90-day window).
- **Latest Performance Hub**: High-density 3-way split showing **Views | Likes | Comments** for your most recent post.
- **Queue Intelligence**: Dynamic **Coverage** calculation—know exactly how many days of automated content you have left.
- **Channel Identity**: Real-time sync with your YouTube profile (Avatar, Title, Subscribers).

### 🚀 Automation Features
- **Instagram-to-Shorts Sync**: Zero-friction downloading and uploading from any Instagram profile.
- **Viral AI Metadata**: 2026-ready, high-CTR hooks and titles generated automatically via LLM.
- **Smart Pacing Engine**: Intelligent 6-hour gaps and daily limits to keep your account safe and relevant.
- **Manual Override**: The "Post Next Reel Now" button gives you instant control, bypassing all scheduling restrictions.

---

## 🛠️ Technical Stack
- **Backend**: FastAPI (Python) with Uvicorn for asynchronous performance.
- **Frontend**: Vanilla HTML5/CSS3/JS with a premium, low-latency "Glassmorphism" UI.
- **APIs**: YouTube Data API v3, Groq/OpenAI (AI Metadata), Instaloader.
- **Security**: OAuth2 token management with local `token.pickle` encryption.

---

## 🚀 Quick Start

### 1. Environment Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration (`.env`)
```env
GROQ_API_KEY=your_key
INSTAGRAM_PROFILE=target_profile
MAX_POSTS_PER_DAY=3
POSTING_GAP_HOURS=6
```

### 3. Launch the Dashboard
```bash
python app.py
```
Visit `http://localhost:8000` to access your Pro-Admin Command Center.

---

## 💡 System Architecture
- `app.py`: High-performance FastAPI dashboard engine.
- `uploader.py`: Robust YouTube integration with 90-day views aggregator.
- `main.py`: The core automation logic and scheduling heartbeat.
- `static/`: Modern, premium-styled dashboard assets.

---

**Built for creators who take automation seriously. Welcome to the Pro-Admin era.** 🎯🔥✨
