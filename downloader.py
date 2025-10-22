import os
import yt_dlp

def download_media(url, format_choice="best"):
    folder = "downloads"
    os.makedirs(folder, exist_ok=True)

    ydl_opts = {
        'outtmpl': f'{folder}/%(title)s.%(ext)s',
        'format': format_choice
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        return file_path
    except Exception as e:
        print(f"Download error: {e}")
        return None
