import os
import yt_dlp
from pytube import YouTube
import instaloader
import asyncio

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

async def download_youtube(url, format_choice="best"):
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'format': format_choice
    }
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))
    except Exception as e:
        # Pytube fallback
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by('resolution').desc().first()
            if not stream:
                return None
            file_path = os.path.join(DOWNLOAD_FOLDER, f"{yt.title}.mp4")
            await loop.run_in_executor(None, lambda: stream.download(output_path=DOWNLOAD_FOLDER, filename=f"{yt.title}.mp4"))
            return file_path
        except Exception as e2:
            print(f"YouTube xato: {e2}")
            return None

async def download_instagram(url):
    L = instaloader.Instaloader(dirname_pattern=DOWNLOAD_FOLDER, download_videos=True, download_comments=False)
    if os.getenv("INSTAGRAM_USERNAME") and os.getenv("INSTAGRAM_PASSWORD"):
        L.login(os.getenv("INSTAGRAM_USERNAME"), os.getenv("INSTAGRAM_PASSWORD"))
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: L.download_post(instaloader.Post.from_shortcode(L.context, url.split("/")[-2]), DOWNLOAD_FOLDER))
        # Qisqa fayl nomini olish (faqat birinchi fayl)
        files = os.listdir(DOWNLOAD_FOLDER)
        files = [f for f in files if f.endswith(('.mp4', '.jpg'))]
        if files:
            return os.path.join(DOWNLOAD_FOLDER, files[-1])
        return None
    except Exception as e:
        print(f"Instagram xato: {e}")
        return None

async def download_media(url):
    if "youtube.com" in url or "youtu.be" in url:
        return await download_youtube(url)
    elif "instagram.com" in url:
        return await download_instagram(url)
    else:
        return None
