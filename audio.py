import os
import subprocess
from aiogram import types, F
from aiogram.types import FSInputFile
from shazamio import Shazam
from pydub import AudioSegment
from bot import bot, dp, DOWNLOAD_PATH
from utils import log_error, update_user_stats, search_youtube, make_song_action_kb, user_search_results, user_pages

# ================= HANDLERS =================
def register_handlers(dp):
    dp.message.register(handle_audio_video, F.voice | F.audio | F.video)

# ================= AUDIO / VIDEO PROCESSING =================
async def handle_audio_video(message: types.Message):
    """
    Audio yoki video faylni qabul qiladi,
    Shazam bilan aniqlaydi,
    MP3 ga konvert qiladi va foydalanuvchiga yuboradi.
    """
    shazam = Shazam()
    status_msg = await message.answer("⏳ Fayl qabul qilinmoqda...")
    
    try:
        # Ovozli fayl
        if message.voice or message.audio:
            file_id = message.voice.file_id if message.voice else message.audio.file_id
            file = await bot.get_file(file_id)
            ogg_path = f"{DOWNLOAD_PATH}/{message.from_user.id}_audio.ogg"
            wav_path = f"{DOWNLOAD_PATH}/{message.from_user.id}_audio.wav"
            await bot.download_file(file.file_path, ogg_path)
            audio = AudioSegment.from_file(ogg_path)
            audio.export(wav_path, format="wav")
            os.remove(ogg_path)

        # Video fayl
        elif message.video:
            file = await bot.get_file(message.video.file_id)
            video_path = f"{DOWNLOAD_PATH}/{message.from_user.id}_video.mp4"
            wav_path = f"{DOWNLOAD_PATH}/{message.from_user.id}_video.wav"
            await bot.download_file(file.file_path, video_path)
            subprocess.run(["ffmpeg", "-y", "-i", video_path, "-vn", "-ac", "2", "-ar", "44100", wav_path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.remove(video_path)
        else:
            await status_msg.edit_text("❌ Fayl topilmadi.")
            return

        # Duration tekshirish
        audio_seg = AudioSegment.from_file(wav_path)
        duration = len(audio_seg) / 1000.0
        if duration < 8:
            os.remove(wav_path)
            await status_msg.edit_text("❌ Audio juda qisqa. Kamida 8 soniya bo'lishi kerak.")
            return

        # Shazam bilan aniqlash
        await status_msg.edit_text("🔍 Shazam tahlil qilmoqda...")
        try:
            shazam_out = await shazam.recognize(wav_path)
        except Exception as e:
            log_error(f"Shazam recognize error: {e}")
            shazam_out = None
        os.remove(wav_path)

        if not shazam_out or not shazam_out.get("track"):
            await status_msg.edit_text("❌ Qo‘shiq topilmadi. Matn orqali nomini yuboring.")
            return

        shazam_title = shazam_out["track"].get("title", "Noma'lum")
        shazam_artist = shazam_out["track"].get("subtitle", "Noma'lum")
        found_song = f"{shazam_artist} - {shazam_title}"

        # Foydalanuvchi statistikasi yangilash
        await update_user_stats(message.from_user.id, message.from_user.username or "", shazam_artist, shazam_title, None)

        # YouTube qidiruvi (topilgan qo‘shiq)
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
