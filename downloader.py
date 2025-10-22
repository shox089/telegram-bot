import os
import yt_dlp
from pytube import YouTube

def download_media(url, format_choice="best"):
    folder = "downloads"
    os.makedirs(folder, exist_ok=True)

    # 🔹 yt-dlp opts
    ydl_opts = {
        'outtmpl': f'{folder}/%(title)s.%(ext)s',
        'format': format_choice
    }

    try:
        # 🔹 Avval yt-dlp bilan yuklash
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        return file_path

    except Exception as e:
        print(f"yt-dlp xatosi: {e}\nPytube bilan yuklashga o‘tayapmiz...")

        # 🔹 Pytube fallback
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by('resolution').desc().first()
            if not stream:
                return None

            file_path = os.path.join(folder, f"{yt.title}.mp4")
            stream.download(output_path=folder, filename=f"{yt.title}.mp4")
            return file_path
        except Exception as e2:
            print(f"Pytube xatosi: {e2}")
            return None
