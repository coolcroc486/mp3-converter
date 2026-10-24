# mp3-converter

A simple web app that converts a YouTube URL into an MP3 file.

How to run

1. Install Python dependencies:
   python -m pip install -r requirements.txt
2. Make sure ffmpeg is installed:
   - macOS: brew install ffmpeg
   - Ubuntu/Debian: sudo apt install ffmpeg
3. Start the app:
   python app.py
4. Open the app in your browser:
   http://localhost:5000
5. Paste a YouTube URL and click "Convert to MP3".

Note

This app uses yt-dlp to download the audio and convert it to MP3 with ffmpeg.
