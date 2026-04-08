from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import threading
import time
import uuid
import re

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = tempfile.mkdtemp()
download_cache = {}  # {task_id: {"status": ..., "file": ..., "title": ..., "error": ...}}


def clean_old_files():
    """Nettoyer les fichiers plus vieux que 10 minutes"""
    while True:
        time.sleep(300)
        now = time.time()
        to_delete = []
        for tid, data in list(download_cache.items()):
            if now - data.get("created_at", now) > 600:
                fpath = data.get("file")
                if fpath and os.path.exists(fpath):
                    os.remove(fpath)
                to_delete.append(tid)
        for tid in to_delete:
            download_cache.pop(tid, None)


threading.Thread(target=clean_old_files, daemon=True).start()


def is_valid_tiktok_url(url):
    patterns = [
        r'https?://(www\.)?tiktok\.com/@[\w.]+/video/\d+',
        r'https?://vm\.tiktok\.com/\w+',
        r'https?://vt\.tiktok\.com/\w+',
        r'https?://m\.tiktok\.com/v/\d+',
    ]
    return any(re.match(p, url) for p in patterns)


def do_download(task_id, url, quality):
    out_template = os.path.join(DOWNLOAD_DIR, f"{task_id}_%(title).50s.%(ext)s")

    ydl_opts = {
        "outtmpl": out_template,
        "quiet": True,
        "no_warnings": True,
    }

    if quality == "audio":
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }]
    else:
        ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "video")

        # Trouver le fichier téléchargé
        for fname in os.listdir(DOWNLOAD_DIR):
            if fname.startswith(task_id):
                fpath = os.path.join(DOWNLOAD_DIR, fname)
                download_cache[task_id].update({
                    "status": "done",
                    "file": fpath,
                    "filename": fname.replace(f"{task_id}_", ""),
                    "title": title,
                })
                return

        download_cache[task_id]["status"] = "error"
        download_cache[task_id]["error"] = "Fichier introuvable après téléchargement."
    except Exception as e:
        download_cache[task_id]["status"] = "error"
        download_cache[task_id]["error"] = str(e)


@app.route("/")
def index():
    with open(os.path.join(os.path.dirname(__file__), "static", "index.html"), encoding="utf-8") as f:
        return f.read()


@app.route("/api/download", methods=["POST"])
def start_download():
    data = request.json or {}
    url = (data.get("url") or "").strip()
    quality = data.get("quality", "video")

    if not url:
        return jsonify({"error": "URL manquante."}), 400

    task_id = str(uuid.uuid4())[:8]
    download_cache[task_id] = {
        "status": "processing",
        "file": None,
        "title": None,
        "error": None,
        "created_at": time.time(),
    }

    t = threading.Thread(target=do_download, args=(task_id, url, quality))
    t.daemon = True
    t.start()

    return jsonify({"task_id": task_id})


@app.route("/api/status/<task_id>")
def check_status(task_id):
    task = download_cache.get(task_id)
    if not task:
        return jsonify({"error": "Tâche introuvable."}), 404
    return jsonify({
        "status": task["status"],
        "title": task["title"],
        "error": task["error"],
    })


@app.route("/api/file/<task_id>")
def get_file(task_id):
    task = download_cache.get(task_id)
    if not task or task["status"] != "done" or not task["file"]:
        return jsonify({"error": "Fichier non disponible."}), 404
    return send_file(
        task["file"],
        as_attachment=True,
        download_name=task.get("filename", "video.mp4"),
    )


if __name__ == "__main__":
    print("🚀 TikTok Downloader lancé sur http://localhost:5000")
    app.run(debug=False, port=5000)