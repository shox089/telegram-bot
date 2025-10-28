import os
import subprocess
from aiogram import types, F
from shazamio import Shazam
from pydub import AudioSegment
from bot import bot, dp, DOWNLOAD_PATH
from utils import log_error, update_user_stats, make_song_action_kb, user_search_results, user_pages
from youtube import search_youtube  # ✅ To‘g‘ri joydan import

# ================= HANDLERS =================
def register_handlers(dp):
    dp.message.register(handle_audio_video, F.voice | F.audio | F.video)

# ================= AUDIO / VIDEO PROCESSING =================
async def handle_audio_video(message: types.Message):
    shazam = Shazam()
    status_msg = await message.answer("⏳ Fayl qabul qilinmoqda...")

    ogg_path = wav_path = video_path = None

    try:
        # ===== Ovozli fayl =====
        if message.voice or message.audio:
            file_id = message.voice.file_id if message.voice else message.audio.file_id
            file = await bot.get_file(file_id)
            ogg_path = os.path.join(DOWNLOAD_PATH, f"{message.from_user.id}_audio.ogg")
            wav_path = os.path.join(DOWNLOAD_PATH, f"{message.from_user.id}_audio.wav")
            await bot.download_file(file.file_path, ogg_path)
            audio = AudioSegment.from_file(ogg_path)
            audio.export(wav_path, format="wav")

        # ===== Video fayl =====
        elif message.video:
            file = await bot.get_file(message.video.file_id)
            video_path = os.path.join(DOWNLOAD_PATH, f"{message.from_user.id}_video.mp4")
            wav_path = os.path.join(DOWNLOAD_PATH, f"{message.from_user.id}_video.wav")
            await bot.download_file(file.file_path, video_path)
            subprocess.run(
                ["ffmpeg", "-y", "-i", video_path, "-vn", "-ac", "2", "-ar", "44100", wav_path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        else:
            await status_msg.edit_text("❌ Fayl topilmadi.")
            return

        # ===== Duration tekshirish =====
        audio_seg = AudioSegment.from_file(wav_path)
        duration = len(audio_seg) / 1000.0
        if duration < 8:
            await status_msg.edit_text("❌ Audio juda qisqa. Kamida 8 soniya bo'lishi kerak.")
            return

        # ===== Shazam bilan aniqlash =====
        await status_msg.edit_text("🔍 Shazam tahlil qilmoqda...")
        try:
            shazam_out = await shazam.recognize(wav_path)
            track_info = shazam_out.get("track", {}) if shazam_out else {}
        except Exception as e:
            log_error(f"Shazam recognize error: {e}")
            track_info = {}

        if not track_info:
            await status_msg.edit_text("❌ Qo‘shiq topilmadi. Matn orqali nomini yuboring.")
            return

        shazam_title = track_info.get("title", "Noma'lum")
        shazam_artist = track_info.get("subtitle", "Noma'lum")
        found_song = f"{shazam_artist} - {shazam_title}"

        # ===== Foydalanuvchi statistikasi =====
        await update_user_stats(message.from_user.id, message.from_user.username or "", shazam_artist, shazam_title, None)

        # ===== YouTube qidiruvi =====
        results = await search_youtube(found_song, limit=1)
        if results:
            user_search_results[message.from_user.id] = results
            user_pages[message.from_user.id] = 0
            res = results[0]
            kb = make_song_action_kb(res["link"], res["title"], shazam_artist)
            caption = f"🎵 <b>{res['title']}</b>\n👤 {shazam_artist}\n✅ Topildi!"
            if res.get("thumbnail"):
                await message.answer_photo(res["thumbnail"], caption=caption, parse_mode="HTML", reply_markup=kb)
            else:
                await message.answer(caption, parse_mode="HTML", reply_markup=kb)
        else:
            await status_msg.edit_text(f"✅ Topildi: {found_song}\n🔎 YouTube natija topilmadi.")

    except Exception as e:
        log_error(f"audio.py error: {e}")
        await status_msg.edit_text("❌ Audio/video bilan ishlashda xatolik yuz berdi.")
    
    finally:
        # ===== Fayllarni xavfsiz o'chirish =====
        for path in [ogg_path, wav_path, video_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass
