from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from urllib.parse import quote_plus
from config import ADMIN_ID

def main_reply_keyboard(user_id):
    kb = [
        [KeyboardButton("▶️ Qidiruv"), KeyboardButton("📂 Tarix / History")],
        [KeyboardButton("👤 Profil"), KeyboardButton("🏆 Top foydalanuvchilar")],
        [KeyboardButton("❤️ Sevimlilar"), KeyboardButton("🌙 Tungi rejim")]
    ]
    if user_id == ADMIN_ID:
        kb.append([KeyboardButton("🔐 Admin panel")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def make_song_action_kb(youtube_url, title, artist):
    payload = quote_plus(f"{title}|||{artist}")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("▶️ Tinglash", url=youtube_url),
         InlineKeyboardButton("❤️ Sevimlilarga qo‘shish", callback_data=f"fav::{payload}")]
    ])
    return kb
