import os
import subprocess
import json
from datetime import datetime
from urllib.parse import quote_plus, unquote_plus

from aiogram import types, F, Dispatcher
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, FSInputFile
from pydub import AudioSegment
from shazamio import Shazam
import matplotlib.pyplot as plt
import aiosqlite

from config import ADMIN_ID, DOWNLOAD_PATH, LOG_FILE, USER_FILE
from utils import log_error, load_json, save_json, clean_filename
from db import update_user_stats
from youtube import search_youtube, download_mp3

# In-memory search
user_search_results = {}   # {user_id: [ {title,link,duration,thumbnail,views,published}, ... ]}
user_pages = {}            # {user_id: page_index}

# ----------------- KEYBOARDS -----------------
def main_reply_keyboard(is_admin=False):
    kb_main_buttons = [
        [KeyboardButton(text="▶️ Qidiruv"), KeyboardButton(text="📂 Tarix / History")],
        [KeyboardButton(text="👤 Profil"), KeyboardButton(text="🏆 Top foydalanuvchilar")],
        [KeyboardButton(text="❤️ Sevimlilar"), KeyboardButton(text="🌙 Tungi rejim")]
    ]
    if is_admin:
        kb_main_buttons.append([KeyboardButton(text="🔐 Admin panel")])
    return ReplyKeyboardMarkup(keyboard=kb_main_buttons, resize_keyboard=True)

def make_song_action_kb(youtube_url: str, title: str, artist: str):
    payload = quote_plus(f"{title}|||{artist}")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="▶️ Tinglash", url=youtube_url),
            InlineKeyboardButton(text="❤️ Sevimlilarga qo‘shish", callback_data=f"fav::{payload}")
        ]
    ])
    return kb

# ----------------- START / LANGUAGE -----------------
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
        kb_main = main_reply_keyboard(message.from_user.id == ADMIN_ID)
        await message.answer("👋 Salom! Nima qilamiz?", reply_markup=kb_main)

async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    users = load_json(USER_FILE)
    users[str(callback.from_user.id)] = users.get(str(callback.from_user.id), {})
    users[str(callback.from_user.id)]["lang"] = lang
    save_json(USER_FILE, users)
    await callback.message.edit_text("✅ Til saqlandi! Endi asosiy menyuga qayting.")

# ----------------- SEARCH RESULTS -----------------
async def show_results(msg: types.Message, user_id: int):
    results = user_search_results.get(user_id, [])
    if not results:
        try:
            await msg.edit_text("❌ Natija topilmadi.")
        except:
            await msg.answer("❌ Natija topilmadi.")
        return
    page = user_pages.get(user_id, 0)
    total_pages = (len(results) + 9) // 10
    start = page * 10
    end = start + 10
    items = results[start:end]

    text = "🎵 <b>Qaysi qo‘shiqni tanlaysiz?</b>\n\n<i>Topilgan qo‘shiqlar:</i>\n\n"
    for i, v in enumerate(items, start=1):
        num = start + i
        text += f"{num}. {v['title']} ({v['duration']}) — {v.get('views','—')}\n"

    buttons = []
    row = []
    for i, v in enumerate(items, start=1):
        num = start + i
        row.append(InlineKeyboardButton(text=f"{num}", callback_data=f"choose::{num}"))
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
    try:
        await msg.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await msg.answer(text, reply_markup=kb, parse_mode="HTML")

async def change_page(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if callback.data == "next_page":
        user_pages[user_id] = user_pages.get(user_id, 0) + 1
    elif callback.data == "prev_page":
        user_pages[user_id] = max(0, user_pages.get(user_id, 0) - 1)
    await show_results(callback.message, user_id)
    await callback.answer()

# ----------------- CHOOSE SONG -----------------
async def choose_callback(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id
        index = int(callback.data.split("::")[1]) - 1
        results = user_search_results.get(user_id)
        if not results or index >= len(results):
            await callback.answer("❌ Topilmadi.")
            return
        song = results[index]
        title = song.get("title")
        link = song.get("link")
        thumbnail = song.get("thumbnail")
        caption = f"🎵 <b>{title}</b>\n🔗 <a href=\"{link}\">YouTube havolasi</a>"
        kb = make_song_action_kb(link, title, "Unknown")

        if thumbnail:
            await callback.message.edit_text("⏳ Ma'lumot olinmoqda...")
            await callback.bot.send_photo(chat_id=user_id, photo=thumbnail, caption=caption, parse_mode="HTML", reply_markup=kb)
        else:
            await callback.message.edit_text(caption, parse_mode="HTML", reply_markup=kb)

        await callback.answer()

        # Download MP3
        await callback.message.answer(f"⏳ <b>{title}</b> yuklanmoqda...", parse_mode="HTML")
        mp3_path = await download_mp3(link)
        if mp3_path:
            try:
                await callback.bot.send_audio(chat_id=user_id, audio=FSInputFile(mp3_path), caption=title)
            except Exception as e:
                log_error(f"send_audio error: {e}")
                try:
                    await callback.bot.send_document(chat_id=user_id, document=FSInputFile(mp3_path), caption=title)
                except Exception as e2:
                    log_error(f"send_document error: {e2}")
            os.remove(mp3_path)
            logs = load_json(LOG_FILE)
            logs.setdefault(str(user_id), []).append(f"{title} — {datetime.now().isoformat()}")
            save_json(LOG_FILE, logs)
            await update_user_stats(user_id, callback.from_user.username or "", "Unknown", title)
            await callback.bot.send_message(user_id, f"✅ <b>{title}</b> MP3 shaklida yuborildi.", parse_mode="HTML")
        else:
            await callback.bot.send_message(user_id, "❌ Yuklashda xatolik yuz berdi.")
    except Exception as e:
        log_error(f"choose_callback error: {e}")
        await callback.answer("❌ Xatolik yuz berdi.")

# ----------------- FAVORITES -----------------
async def add_to_favorites(callback: types.CallbackQuery):
    try:
        payload = callback.data.split("::", 1)[1]
        decoded = unquote_plus(payload)
        title, artist = decoded.split("|||", 1)
        user_id = callback.from_user.id
        async with aiosqlite.connect("musicbot.sqlite") as db:
            await db.execute("INSERT OR IGNORE INTO favorites (user_id, title, artist) VALUES (?, ?, ?)", (user_id, title, artist))
            await db.commit()
        users = load_json(USER_FILE)
        u = users.get(str(user_id), {})
        favs = u.get("fav", [])
        if title not in favs:
            favs.append(title)
            u["fav"] = favs
            users[str(user_id)] = u
            save_json(USER_FILE, users)
        await callback.answer("❤️ Sevimlilarga qo‘shildi!", show_alert=True)
    except Exception as e:
        log_error(str(e))
        await callback.answer("❌ Sevimlilarga qo‘shishda xatolik.", show_alert=True)

async def show_favorites(message: types.Message):
    user_id = message.from_user.id
    async with aiosqlite.connect("musicbot.sqlite") as db:
        cur = await db.execute("SELECT title, artist FROM favorites WHERE user_id=? ORDER BY id DESC LIMIT 50", (user_id,))
        rows = await cur.fetchall()
    if not rows:
        await message.answer("❤️ Sizda hali sevimli qo‘shiqlar yo‘q.")
        return
    text = "❤️ <b>Sevimli qo‘shiqlaringiz:</b>\n\n"
    for i, (title, artist) in enumerate(rows, start=1):
        text += f"{i}. {title} — {artist}\n"
    await message.answer(text, parse_mode="HTML")

# ----------------- REGISTER HANDLERS -----------------
def register_handlers(dp: Dispatcher):
    dp.message.register(start_cmd, Command("start"))
    dp.callback_query.register(set_language, F.data.startswith("lang_"))
    dp.callback_query.register(change_page, F.data.in_(["next_page","prev_page"]))
    dp.callback_query.register(choose_callback, F.data.startswith("choose::"))
    dp.callback_query.register(add_to_favorites, F.data.startswith("fav::"))
    dp.message.register(show_favorites, lambda m: m.text in ["❤️ Sevimlilar","/fav"])
