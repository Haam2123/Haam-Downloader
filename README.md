# Video Downloader (Flask + yt-dlp)

A simple web UI to download videos from many sites using **yt-dlp**.

> ⚠️ Respect each website's Terms of Service and local laws. Download only content you have the right to save.

## Features
- Flask backend with background download threads
- Progress/status API
- Tailwind frontend with progress bar
- Dockerfile for easy deploy
- Render config (`render.yaml`) and Procfile for non-Docker deploys
- Optional persistent disk for downloads

## Local Run

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:5000
```

## Deploy to Render (from GitHub)

### Option A — Non‑Docker (simplest)
1. Push this project to a **public or private GitHub repo**.
2. Ensure these files are present:
   - `requirements.txt`
   - `Procfile`
   - `apt.txt` (so Render installs `ffmpeg` automatically)
   - `app.py` (binds to `$PORT`)
3. In Render, click **New → Web Service** → **Build & deploy from a Git repository** → connect your repo.
4. Set **Environment** to `Python`.
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `gunicorn app:app --workers 2 --threads 4 --timeout 120 -b 0.0.0.0:$PORT`
7. (Optional) **Add a persistent disk**:
   - Name: `downloads`, Mount Path: `/app/downloads`, Size: `1GB+`
8. Click **Create Web Service**. Your app will build and deploy. Every push to GitHub auto‑deploys.

### Option B — Docker
1. Keep the included `Dockerfile`.
2. In Render, choose **New → Web Service** → **Docker** → connect your repo.
3. Render will build your Docker image and run `CMD ["python", "app.py"]`.
4. Ensure your app listens on `$PORT` (this repo's `app.py` already does).

## Repository Structure

```
.
├─ app.py
├─ templates/
│  └─ index.html
├─ downloads/            # runtime files (gitignored)
├─ requirements.txt
├─ Dockerfile
├─ Procfile
├─ render.yaml
├─ apt.txt
├─ .gitignore
└─ README.md
```

## Notes
- The in‑memory task tracker resets on restart. For multi‑instance or long‑term state, plug in Redis.
- If using a persistent disk, files accumulate; consider periodic cleanup.
- To customize formats, edit `yt_dlp` options in `app.py`.