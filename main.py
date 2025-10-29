import os
import re
import json
import asyncio
import subprocess
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch
from shazamio import Shazam
from pydub import AudioSegment

# 🔹 Bot tokeni va admin
API_TOKEN = "8485966159:AAE63BOncpVTfzN7NL04Em5DUTK05HXUjnE"
ADMIN_ID = 6688725338

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Pella serverda faqat /tmp papkaga yozish mumkin
DOWNLOAD_PATH = "/tmp/downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

LOG_FILE = "/tmp/downloads_log.json"
USER_FILE = "/tmp/users.json"
ERROR_LOG = "/tmp/errors.log"

user_search_results = {}
user_pages = {}

# ---------- Yordamchi funksiyalar ----------
def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|,]', "", name)

def log_error(error_text):
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"[ERROR] {error_text}\n")

# ---------- /start ----------
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    users = load_json(USER_FILE)
    user_id = str(message.from_user.id)
    if user_id not in users:
        kb_lang = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇿 O‘zbek", callback_data="lang_uz")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
        ])
        await message.answer("🌍 Tilni tanlang / Выберите язык / Choose language:", reply_markup=kb_lang)
    else:
        kb_main_buttons = [
            [KeyboardButton(text="▶️ Qidiruv")],
            [KeyboardButton(text="📂 Tarix / History")]
        ]
        if message.from_user.id == ADMIN_ID:
            kb_main_buttons.append([KeyboardButton(text="🔐 Admin panel")])
        kb_main = ReplyKeyboardMarkup(keyboard=kb_main_buttons, resize_keyboard=True)
        await message.answer("👋 Salom! Nima qilamiz?", reply_markup=kb_main)

# ---------- Til tanlash ----------
@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    users = load_json(USER_FILE)
    users[str(callback.from_user.id)] = {"lang": lang}
    save_json(USER_FILE, users)
    await callback.message.edit_text("✅ Til saqlandi! Endi asosiy menyuga qayting.")

# ---------- YouTube qidiruv ----------
async def search_youtube(query, limit=20):
    search = VideosSearch(query, limit=limit)
    results = search.result()["result"]
    return [{"title": clean_filename(v["title"]), "link": v["link"], "duration": v.get("duration", "unknown")} for v in results]

# ---------- /history ----------
async def show_history(message: types.Message):
    logs = load_json(LOG_FILE)
    user_logs = logs.get(str(message.from_user.id), [])
    if not user_logs:
        await message.answer("📂 Siz hali hech narsa yuklamagansiz.")
        return
    text = "🕘 <b>So‘nggi 5 ta yuklab olingan qo‘shiqlar:</b>\n\n"
    for i, song in enumerate(user_logs[-5:], 1):
        text += f"{i}. {song}\n"
    await message.answer(text, parse_mode="HTML")

# ---------- Qo‘shiq ro‘yxatini chiqarish ----------
async def show_results(msg, user_id):
    results = user_search_results[user_id]
    page = user_pages.get(user_id, 0)
    total_pages = (len(results) + 9) // 10
    start = page * 10
    end = start + 10
    items = results[start:end]

    text = "🎵 <b>Qaysi qo‘shiqni tanlaysiz?</b>\n\n<i>Topilgan qo‘shiqlar:</i>\n\n"
    for i, v in enumerate(items, start=1):
        num = start + i
        text += f"{num}. {v['title']} ({v['duration']})\n"

    buttons = []
    row = []
    for i, v in enumerate(items, start=1):
        num = start + i
        row.append(InlineKeyboardButton(text=f"{num}", callback_data=f"download_{num}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="prev_page"))
    if end < len(results):
        nav_buttons.append(InlineKeyboardButton(text="➡️ Keyingi", callback_data="next_page"))
    if nav_buttons:
        buttons.append(nav_buttons)

    text += f"\n📄 <i>{page + 1}/{total_pages} sahifa</i>"
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await msg.edit_text(text, reply_markup=kb, parse_mode="HTML")

# ---------- Sahifalar navigatsiyasi ----------
@dp.callback_query(F.data.in_(["next_page", "prev_page"]))
async def change_page(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_search_results:
        await callback.answer("❌ Avval qidiruv qiling.")
        return
    if callback.data == "next_page":
        user_pages[user_id] += 1
    elif callback.data == "prev_page":
        user_pages[user_id] -= 1
    await show_results(callback.message, user_id)
    await callback.answer()

# ---------- Yuklab olish ----------
@dp.callback_query(F.data.startswith("download_"))
async def download_song(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    index = int(callback.data.split("_")[1]) - 1
    results = user_search_results.get(user_id)
    if not results or index >= len(results):
        await callback.answer("❌ Qo‘shiq topilmadi.")
        return
    song = results[index]
    title = song["title"]
    url = song["link"]
    msg = await callback.message.edit_text(f"⏳ Yuklanmoqda...\n<b>{title}</b>", parse_mode="HTML")
    ydl_opts = {"outtmpl": f"{DOWNLOAD_PATH}/%(title)s.%(ext)s", "format": "bestaudio/best", "quiet": True, "noplaylist": True}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        mp3_path = os.path.splitext(file_path)[0] + ".mp3"
        subprocess.run(["ffmpeg", "-y", "-i", file_path, "-vn", "-ab", "192k", "-ar", "44100", mp3_path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(file_path)
        await bot.send_audio(chat_id=user_id, audio=FSInputFile(mp3_path), caption=title)
        os.remove(mp3_path)
        logs = load_json(LOG_FILE)
        logs.setdefault(str(user_id), []).append(title)
        save_json(LOG_FILE, logs)
        await msg.edit_text("✅ Yuklab olindi!", parse_mode="HTML")
    except Exception as e:
        log_error(str(e))
        await msg.edit_text(f"❌ Xatolik: {e}")

# ---------- ADMIN PANEL ----------
async def handle_admin_panel(message: types.Message):
    if message.text != "🔐 Admin panel" or message.from_user.id != ADMIN_ID:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="🎧 Oxirgi yuklamalar", callback_data="admin_downloads")],
        [InlineKeyboardButton(text="⚠️ Xatoliklar", callback_data="admin_errors")]
    ])
    await message.answer("🔐 Admin panelga xush kelibsiz:", reply_markup=kb)

@dp.callback_query(F.data.startswith("admin_"))
async def admin_buttons(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Bu bo‘lim faqat admin uchun.", show_alert=True)
        return
    data = callback.data
    if data == "admin_stats":
        users = load_json(USER_FILE)
        logs = load_json(LOG_FILE)
        total_users = len(users)
        total_downloads = sum(len(v) for v in logs.values())
        text = (f"📊 <b>Statistika:</b>\n\n👤 Foydalanuvchilar: <b>{total_users}</b>\n"
                f"🎧 Yuklab olishlar: <b>{total_downloads}</b>\n"
                f"🗓️ O‘rtacha yuklamalar: {total_downloads / total_users if total_users else 0:.1f}")
        await callback.message.edit_text(text, parse_mode="HTML")
    elif data == "admin_downloads":
        logs = load_json(LOG_FILE)
        all_songs = [song for user_songs in logs.values() for song in user_songs]
        last_songs = all_songs[-10:] if all_songs else []
        if not last_songs:
            await callback.message.edit_text("📂 Hozircha hech narsa yuklab olinmagan.")
            return
        text = "🎶 <b>So‘nggi 10 ta yuklab olingan qo‘shiqlar:</b>\n\n"
        for i, song in enumerate(last_songs, 1):
            text += f"{i}. {song}\n"
        await callback.message.edit_text(text, parse_mode="HTML")
    elif data == "admin_errors":
        if not os.path.exists(ERROR_LOG):
            await callback.message.edit_text("✅ Hozircha xatoliklar yo‘q.")
            return
        with open(ERROR_LOG, "r", encoding="utf-8") as f:
            errors = f.readlines()[-10:]
        if not errors:
            await callback.message.edit_text("✅ Hozircha xatoliklar yo‘q.")
            return
        text = "⚠️ <b>So‘nggi xatoliklar:</b>\n\n" + "".join(errors)
        await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

# ---------- Asosiy handler ----------
@dp.message()
async def handle_message(message: types.Message):
    try:
        if message.text:
            if message.text == "📂 Tarix / History":
                await show_history(message)
                return
            if message.text == "🔐 Admin panel" and message.from_user.id == ADMIN_ID:
                await handle_admin_panel(message)
                return
            if message.text == "▶️ Qidiruv":
                await message.answer("🔎 Iltimos, qo‘shiq nomini yozing yoki audio/video yuboring.")
                return

        # ---------- AUDIO / VOICE ----------
        if message.voice or message.audio:
            shazam = Shazam()
            status_msg = await message.answer("⏳ Audio qabul qilinmoqda...")
            file_id = message.voice.file_id if message.voice else message.audio.file_id
            file = await bot.get_file(file_id)
            ogg_path = f"{DOWNLOAD_PATH}/{message.from_user.id}_audio.ogg"
            wav_path = f"{DOWNLOAD_PATH}/{message.from_user.id}_audio.wav"
            await bot.download_file(file.file_path, ogg_path)
            audio = AudioSegment.from_file(ogg_path)
            audio.export(wav_path, format="wav")
            os.remove(ogg_path)
            duration = len(audio) / 1000
            if duration < 10:
                os.remove(wav_path)
                await status_msg.edit_text("❌ Ovozli fayl juda qisqa. Kamida 10 soniya audio yuboring.")
                return
            await status_msg.edit_text("🔍 Shazam tahlil qilmoqda...")
            shazam_out = await shazam.recognize(wav_path)
            os.remove(wav_path)
            shazam_title = shazam_out["track"]["title"]
            shazam_artist = shazam_out["track"]["subtitle"]
            found_song = f"{shazam_artist} - {shazam_title}"
            fallback_query = shazam_title
            try:
                results = await search_youtube(found_song)
                if not results:
                    raise ValueError("YouTube natija topilmadi")
                user_search_results[message.from_user.id] = results
                user_pages[message.from_user.id] = 0
                await status_msg.edit_text(f"✅ Topildi: {found_song}\n🔎 YouTube’da qidirilmoqda...")
                await show_results(status_msg, message.from_user.id)
            except Exception as e:
                log_error(str(e))
                fallback_results = await search_youtube(fallback_query)
                if fallback_results:
                    user_search_results[message.from_user.id] = fallback_results
                    user_pages[message.from_user.id] = 0
                    await status_msg.edit_text(
                        f"❌ Xatolik yuz berdi. Admin bu haqida xabardor qilindi.\n"
                        f"📄 Siz yozgandek qo‘shiq nomi: {found_song}\n"
                        "🔹 YouTube fallback qidiruvi..."
                    )
                    await show_results(status_msg, message.from_user.id)
            return

        # ---------- VIDEO ----------
        if message.video:
            shazam = Shazam()
            status_msg = await message.answer("⏳ Video qabul qilinmoqda...")
            file_id = message.video.file_id
            file = await bot.get_file(file_id)
            video_path = f"{DOWNLOAD_PATH}/{message.from_user.id}_video.mp4"
            wav_path = f"{DOWNLOAD_PATH}/{message.from_user.id}_video.wav"
            await bot.download_file(file.file_path, video_path)

            # Video -> Audio (.wav)
            subprocess.run(["ffmpeg", "-y", "-i", video_path, "-vn", "-ac", "2", "-ar", "44100", wav_path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.remove(video_path)

            audio = AudioSegment.from_file(wav_path)
            duration = len(audio) / 1000
            if duration < 10:
                os.remove(wav_path)
                await status_msg.edit_text("❌ Video audiosi juda qisqa. Kamida 10 soniya bo‘lishi kerak.")
                return

            await status_msg.edit_text("🔍 Shazam tahlil qilmoqda...")
            shazam_out = await shazam.recognize(wav_path)
            os.remove(wav_path)
            shazam_title = shazam_out["track"]["title"]
            shazam_artist = shazam_out["track"]["subtitle"]
            found_song = f"{shazam_artist} - {shazam_title}"
            fallback_query = shazam_title

            try:
                results = await search_youtube(found_song)
                if not results:
                    raise ValueError("YouTube natija topilmadi")
                user_search_results[message.from_user.id] = results
                user_pages[message.from_user.id] = 0
                await status_msg.edit_text(f"✅ Topildi: {found_song}\n🔎 YouTube’da qidirilmoqda...")
                await show_results(status_msg, message.from_user.id)
            except Exception as e:
                log_error(str(e))
                fallback_results = await search_youtube(fallback_query)
                if fallback_results:
                    user_search_results[message.from_user.id] = fallback_results
                    user_pages[message.from_user.id] = 0
                    await status_msg.edit_text(
                        f"❌ Xatolik yuz berdi. Admin bu haqida xabardor qilindi.\n"
                        f"📄 Siz yozgandek qo‘shiq nomi: {found_song}\n"
                        "🔹 YouTube fallback qidiruvi..."
                    )
                    await show_results(status_msg, message.from_user.id)
            return

        # ---------- MATN Qidiruv ----------
        if message.text:
            query = message.text.strip()
            status_msg = await message.answer(f"🔎 Qidirilmoqda: {query}")
            try:
                results = await search_youtube(query)
                if not results:
                    raise ValueError("YouTube natija topilmadi")
                user_search_results[message.from_user.id] = results
                user_pages[message.from_user.id] = 0
                await show_results(status_msg, message.from_user.id)
            except Exception as e:
                log_error(str(e))
                fallback_query = query.split("-")[-1].strip() if "-" in query else query
                fallback_results = await search_youtube(fallback_query)
                if fallback_results:
                    user_search_results[message.from_user.id] = fallback_results
                    user_pages[message.from_user.id] = 0
                    await status_msg.edit_text(
                        f"❌ Xatolik yuz berdi. Admin bu haqida xabardor qilindi.\n"
                        f"📄 Siz yozgandek qo‘shiq nomi: {query}\n"
                        "🔹 YouTube fallback qidiruvi..."
                    )
                    await show_results(status_msg, message.from_user.id)

    except Exception as e:
        log_error(str(e))
        await message.answer("❌ Xatolik yuz berdi. Admin bu haqida xabardor qilindi.")

# ---------- Ishga tushirish ----------
async def main():
    print("🤖 Shazam bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
