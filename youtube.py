import os
import asyncio
from youtubesearchpython import VideosSearch
import yt_dlp
from aiogram import types
from utils import clean_filename, log_error
from config import DOWNLOAD_PATH

# Ensure download path exists
os.makedirs(DOWNLOAD_PATH, exist_ok=True)


# ---------------------------
# YouTube qidiruv funksiyasi
# ---------------------------
async def search_youtube(query: str, limit: int = 10):
    """
    YouTube'dan video qidiradi va natijalarni qaytaradi
    (VideosSearch sync API, shuning uchun to'g'ridan-to'g'ri chaqiriladi)
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
            views = (
                v.get("viewCount", {}).get("text")
                if isinstance(v.get("viewCount"), dict)
                else v.get("viewCount") or "—"
            )
            published = v.get("publishedTime") or v.get("published") or v.get("uploadedOn") or "—"

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
# YouTube MP3 yuklash va yuborish
# ---------------------------
async def download_mp3_and_send(url: str, message: types.Message):
    """
    YouTube videoni MP3 formatida yuklab, foydalanuvchiga yuboradi.
    yt-dlp bloklovchi bo'lgani uchun download qismi executorda ishlaydi.
    """
    try:
        # 1) Info olish (bloklovchi, lekin juda kichik, shuning uchun ham executorga joylash mumkin)
        loop = asyncio.get_running_loop()
        try:
            info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL({'quiet': True}).extract_info(url, download=False))
        except Exception as e:
            # Agar info olishda muammo bo'lsa, log va xabar
            log_error(f"yt_dlp.extract_info error for {url}: {e}")
            await message.answer("❌ Video ma'lumotlarini olishda xatolik. Iltimos, URLni tekshiring.")
            return

        # title va id olish
        raw_title = info.get('title', 'unknown')
        safe_title = clean_filename(raw_title)
        vid_id = info.get('id') or safe_title

        # 2) outtmpl bilan aniqlik
        # biz id asosida nomlaymiz: <DOWNLOAD_PATH>/<id>.%(ext)s  -> keyin .mp3 bo'ladi
        outtmpl = os.path.join(DOWNLOAD_PATH, f"{vid_id}.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }

        # 3) yuklash (bloklovchi) -> executorda bajariladi
        def run_download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        await loop.run_in_executor(None, run_download)

        # 4) natijaviy mp3 yo'li
        mp3_path = os.path.join(DOWNLOAD_PATH, f"{vid_id}.mp3")

        if not os.path.exists(mp3_path):
            # ba'zan ffmpeg yoki postprocessor muvaffaqiyatsiz bo'lishi mumkin
            log_error(f"MP3 fayli topilmadi: expected {mp3_path}")
            await message.answer("❌ Yuklash muvaffaqiyatsiz tugadi (fayl topilmadi).")
            return

        # 5) yuborish
        await message.answer_document(types.InputFile(mp3_path), caption=f"🎧 {safe_title}")

        # 6) tozalash: faylni o'chirish
        try:
            os.remove(mp3_path)
        except Exception as e:
            log_error(f"Failed to remove file {mp3_path}: {e}")

    except Exception as e:
        log_error(f"download_mp3_and_send error: {e}")
        # qo'shimcha xabar foydalanuvchiga
        try:
            await message.answer("Xatolik yuz berdi, iltimos keyinroq urinib ko‘ring.")
        except:
            pass
