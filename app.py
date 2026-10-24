from flask import Flask, render_template, request, send_from_directory, url_for
from pathlib import Path
import os
import re
import subprocess

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

app.config["DOWNLOAD_FOLDER"] = str(DOWNLOAD_DIR)


def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9 _\-\.]+", "", name or "youtube_audio")
    return cleaned.strip() or "youtube_audio"


def find_latest_mp3() -> str | None:
    files = sorted(DOWNLOAD_DIR.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0].name if files else None


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    success = None
    filename = None
    download_url = None

    if request.method == "POST":
        video_url = (request.form.get("url") or "").strip()

        if not video_url:
            error = "Please paste a YouTube URL first."
        else:
            try:
                # Download audio in mp3 format into the downloads folder.
                subprocess.run(
                    [
                        "yt-dlp",
                        "-f",
                        "bestaudio/best",
                        "--extract-audio",
                        "--audio-format",
                        "mp3",
                        "--audio-quality",
                        "0",
                        "-o",
                        str(DOWNLOAD_DIR / "%(title)s.%(ext)s"),
                        video_url,
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

                info = subprocess.run(
                    ["yt-dlp", "--get-title", video_url],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                title = sanitize_filename(info.stdout.strip())

                # Try to find the most recently created mp3 file.
                newest = find_latest_mp3()
                if newest:
                    filename = newest
                    download_url = url_for("download_file", filename=filename)
                    success = f"Your MP3 is ready."
                else:
                    error = "The conversion finished, but no MP3 file was created."

            except subprocess.CalledProcessError:
                error = "The download failed. Check the URL or make sure ffmpeg and yt-dlp are installed."

    return render_template(
        "index.html",
        error=error,
        success=success,
        filename=filename,
        download_url=download_url,
    )


@app.route("/download/<path:filename>")
def download_file(filename: str):
    return send_from_directory(app.config["DOWNLOAD_FOLDER"], filename, as_attachment=True)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
