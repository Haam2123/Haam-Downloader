from flask import Flask, request, jsonify, send_file, render_template
import os
import threading
import uuid
import yt_dlp
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
# Use a random secret key each run; set a fixed one via env in production if you prefer
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", os.urandom(24))

# Directory for downloads (mount a persistent disk here in production if desired)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# In-memory task tracker (for a single process instance)
tasks = {}

def progress_hook(d, task_id):
    """Update task progress information in memory."""
    if d.get("status") == "downloading":
        tasks[task_id]["status"] = "downloading"
        tasks[task_id]["progress"] = d.get("_percent_str", "").strip()
        tasks[task_id]["speed"] = d.get("_speed_str", "")
        tasks[task_id]["eta"] = d.get("eta", "")
    elif d.get("status") == "finished":
        tasks[task_id]["status"] = "processing"

def download_video(task_id, url):
    """Background video download using yt-dlp."""
    task = tasks[task_id]
    try:
        # Create unique, safe output template
        safe_name = secure_filename(url)[:50] or "download"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outtmpl = os.path.join(DOWNLOAD_DIR, f"{safe_name}_{timestamp}.%(ext)s")

        ydl_opts = {
            "outtmpl": outtmpl,
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "progress_hooks": [lambda d: progress_hook(d, task_id)],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Find the produced file (common extensions)
        for ext in ["mp4", "mkv", "webm", "mov"]:
            path = outtmpl.replace("%(ext)s", ext)
            if os.path.exists(path):
                task["file_path"] = path
                break

        task["status"] = "finished"

    except Exception as e:
        task["status"] = "error"
        task["error"] = str(e)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def start_download():
    data = request.get_json(silent=True) or {}
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "queued",
        "progress": None,
        "speed": None,
        "eta": None,
        "file_path": None,
        "error": None,
    }

    threading.Thread(target=download_video, args=(task_id, url), daemon=True).start()
    return jsonify({"task_id": task_id}), 202

@app.route("/status/<task_id>", methods=["GET"])
def check_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Invalid task ID"}), 404
    return jsonify(task)

@app.route("/file/<task_id>", methods=["GET"])
def get_file(task_id):
    task = tasks.get(task_id)
    if not task or not task.get("file_path"):
        return jsonify({"error": "File not ready"}), 404
    # as_attachment triggers a download in the browser
    return send_file(task["file_path"], as_attachment=True)

if __name__ == "__main__":
    # Bind to the port provided by the environment (Render/Heroku), default to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
