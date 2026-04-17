from flask import Flask, request, jsonify, render_template
import yt_dlp
import threading
import os

app = Flask(__name__)

progress_data = {"status": ""}

# create downloads folder
if not os.path.exists("downloads"):
    os.makedirs("downloads")

@app.route('/')
def home():
    return render_template("index.html")

# progress hook
def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%')
        progress_data["status"] = f"Downloading... {percent}"
    elif d['status'] == 'finished':
        progress_data["status"] = "Processing..."

# download function
def download_video(url, quality):
    if quality == "720":
        format_code = "bestvideo[height<=720]+bestaudio/best"
    elif quality == "audio":
        format_code = "bestaudio/best"
    else:
        format_code = "bestvideo[height<=1080]+bestaudio/best"

    ydl_opts = {
        'format': format_code,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'progress_hooks': [progress_hook]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    progress_data["status"] = "Download completed!"

# API
@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get("url")
    quality = data.get("quality")

    threading.Thread(target=download_video, args=(url, quality)).start()

    return jsonify({"message": "Download started!"})

# progress API
@app.route('/progress')
def progress():
    return jsonify(progress_data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)