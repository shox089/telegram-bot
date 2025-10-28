import os
import asyncio
from youtubesearchpython import VideosSearch
import yt_dlp
from aiogram import types
from utils import clean_filename, log_error, log_download
from config import DOWNLOAD_PATH

# Yuklash papkasini yaratish
os.makedirs(DOWNLOAD_PATH, exist_ok=True)


# ---------------------------
# 🔍 YouTube qidiruv funksiyasi
# ---------------------------
async def search_youtube(query: str, limit: int = 10):
    """
    YouTube'dan video qidiradi va natijalarni qaytaradi.
    """
    try:
        search = VideosSearch(query, limit=limit)
        items = search.result().get("result", [])
        results = []

        for v in items:
            title = v.get("title")
            link = v.get("link")
            if not title or not link:
                continue

            duration = v.get("duration", "—")
            thumb = v.get("thumbnails", [{}])[0].get("url")
            views = (
                v.get("viewCount", {}).get("text")
                if isinstance(v.get("viewCount"), dict)
                else v.get("viewCount") or "—"
            )
            published = (
                v.get("publishedTime")
                or v.get("published")
                or v.get("uploadedOn")
                or "—"
            )

            results.append(
                {
                    "title": clean_filename(title),
                    "link": link,
                    "duration": duration,
                    "thumbnail": thumb,
                    "views": views,
                    "published": published,
                }
            )

        return results

    except Exception as e:
        log_error(f"search_youtube error: {e}")
        return []


# ---------------------------
# 🎧 YouTube MP3 yuklab yuborish
# ---------------------------
async def download_mp3_and_send(url: str, message: types.Message):
    """
    YouTube videoni MP3 formatida yuklab, foydalanuvchiga yuboradi.
    """
    try:
        loop = asyncio.get_running_loop()

        # 🔹 Videoinfo olish
        try:
            info = await loop.run_in_executor(
                None,
                lambda: yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}).extract_info(url, download=False),
            )
        except Exception as e:
            log_error(f"yt_dlp.extract_info error for {url}: {e}")
            await message.answer("❌ Video ma'lumotlarini olishda xatolik yuz berdi.")
            return

        title = clean_filename(info.get("title", "unknown"))
        vid_id = info.get("id") or title
        mp3_path = os.path.join(DOWNLOAD_PATH, f"{vid_id}.mp3")

        # 🔹 Yuklash sozlamalari
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(DOWNLOAD_PATH, f"{vid_id}.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "quiet": True,
            "no_warnings": True,
        }

        # 🔹 Yuklash
        def run_download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        await message.answer("🎵 Yuklab olinmoqda, biroz kuting...")
        await loop.run_in_executor(None, run_download)

        if not os.path.exists(mp3_path):
            log_error(f"MP3 not found after download: {mp3_path}")
            await message.answer("❌ Yuklash muvaffaqiyatsiz tugadi (fayl topilmadi).")
            return

        # 🔹 Foydalanuvchiga yuborish
        await message.answer_document(
            types.InputFile(mp3_path),
            caption=f"🎧 {title}\n\n✅ Yuklab olindi YouTube'dan.",
        )

        # 🔹 Tarixga yozish
        await log_download(
            message.from_user.id,
            {"title": title, "url": url, "source": "YouTube", "file": mp3_path},
        )

        # 🔹 Faylni o‘chirish
        try:
            os.remove(mp3_path)
        except Exception as e:
            log_error(f"Failed to remove {mp3_path}: {e}")

    except Exception as e:
        log_error(f"download_mp3_and_send error: {e}")
        try:
            await message.answer("❌ Yuklab olishda xatolik yuz berdi.")
        except:
            pass
