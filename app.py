from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
from yt_dlp import YoutubeDL
import uuid
import glob

app = Flask(__name__)
app.secret_key = "random_secret_key"
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_media(url, mode):
    uid = str(uuid.uuid4())
    filename = os.path.join(DOWNLOAD_FOLDER, f"{uid}.%(ext)s")

    ydl_opts = {
        "outtmpl": filename,
        "quiet": True,
        "noplaylist": True,
    }

    if mode == "audio":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
        extension = ".mp3"
    elif mode == "thumbnail":
        ydl_opts.update({
            "skip_download": True,
            "writethumbnail": True,
        })
        extension = ".jpg"
    else:
        ydl_opts["format"] = "best"
        extension = ".mp4"

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return None, str(e)

    # Find the downloaded file
    files = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"{uid}*"))
    if not files:
        return None, "File tidak ditemukan."

    return files[0], None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        mode = request.form.get("mode")

        if not url:
            flash("URL tidak boleh kosong!", "error")
            return redirect(url_for("index"))

        file_path, error = download_media(url, mode)
        if error:
            flash(f"Gagal mengunduh: {error}", "error")
            return redirect(url_for("index"))

        return send_file(file_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
