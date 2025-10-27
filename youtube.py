import os
from youtubesearchpython import VideosSearch
import yt_dlp
from aiogram import types
from utils import clean_filename, log_error
from config import DOWNLOAD_PATH

# ---------------------------
# YouTube qidiruv funksiyasi
# ---------------------------
async def search_youtube(query, limit=10):
    """
    YouTube'dan video qidiradi va natijalarni qaytaradi
    """
    try:
        search = VideosSearch(query, limit=limit)
        items = search.result().get("result", [])
        results = []

        for v in items:
            title, link = v.get("title"), v.get("link")
            if not title or not link:
                continue

            duration = v.get("duration", "—")
            thumb = v.get("thumbnails")[0]["url"] if v.get("thumbnails") else None
            views = v.get("viewCount", {}).get("text") if isinstance(v.get("viewCount"), dict) else v.get("viewCount") or "—"
            published = v.get("publishedTime") or v.get("published") or v.get("uploadedOn") or "—"

            results.append({
                "title": clean_filename(title),
                "link": link,
                "duration": duration,
                "thumbnail": thumb,
                "views": views,
                "published": published
            })

        return results

    except Exception as e:
        log_error(f"search_youtube error: {e}")
        return []

# ---------------------------
# YouTube MP3 yuklash va yuborish
# ---------------------------
async def download_mp3_and_send(url: str, message: types.Message):
    """
    YouTube videoni MP3 formatida yuklab, foydalanuvchiga yuboradi
    """
    try:
        # Video ma'lumotlarini olish
        info = yt_dlp.YoutubeDL({'quiet': True}).extract_info(url, download=False)
        title = clean_filename(info.get('title', 'unknown'))

        # Papka mavjudligini tekshirish
        os.makedirs(DOWNLOAD_PATH, exist_ok=True)
        filepath = os.path.join(DOWNLOAD_PATH, f"{title}.mp3")

        # YT-DLP opsiyalari
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filepath,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True
        }

        # Yuklash
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Foydalanuvchiga yuborish
        await message.answer_document(types.InputFile(filepath))

    except Exception as e:
        log_error(f"download_mp3_and_send error: {e}")
        await message.answer("Xatolik yuz berdi, iltimos keyinroq urinib ko‘ring.")
