from flask import Flask, request, jsonify, render_template, send_from_directory
import yt_dlp
import threading
import os

app = Flask(__name__)

# create downloads folder
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# global progress
progress_data = {"percent": 0, "status": ""}


@app.route('/')
def home():
    return render_template("index.html")


def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%')
        progress_data["percent"] = percent
        progress_data["status"] = "Downloading..."
    elif d['status'] == 'finished':
        progress_data["percent"] = "100%"
        progress_data["status"] = "Completed"


def download_video(url, quality):
    progress_data["percent"] = "0%"
    progress_data["status"] = "Starting..."

    if quality == "audio":
        format_code = "bestaudio"
    elif quality == "720p":
        format_code = "bestvideo[height<=720]+bestaudio/best"
    else:
        format_code = "bestvideo[height<=1080]+bestaudio/best"

    ydl_opts = {
        'format': format_code,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'progress_hooks': [progress_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get("url")
    quality = data.get("quality")

    try:
        threading.Thread(target=download_video, args=(url, quality)).start()
        return jsonify({"message": "Download started!"})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/progress')
def progress():
    return jsonify(progress_data)


@app.route('/files')
def files():
    return jsonify(os.listdir("downloads"))


@app.route('/download_file/<filename>')
def download_file(filename):
    return send_from_directory("downloads", filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)