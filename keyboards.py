from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from urllib.parse import quote_plus
from config import ADMIN_USERNAME


# ---------------------------
# 📱 Asosiy menyu klaviaturasi
# ---------------------------
def main_reply_keyboard(current_username: str = None) -> ReplyKeyboardMarkup:
    """
    Asosiy menyu klaviaturasini yaratadi.
    Agar foydalanuvchi admin bo‘lsa, qo‘shimcha tugma qo‘shiladi.
    """
    kb = [
        [KeyboardButton("▶️ Qidiruv"), KeyboardButton("📂 Tarix / History")],
        [KeyboardButton("👤 Profil"), KeyboardButton("🏆 Top foydalanuvchilar")],
        [KeyboardButton("❤️ Sevimlilar"), KeyboardButton("🌙 Tungi rejim")]
    ]
    if current_username and current_username == ADMIN_USERNAME:
        kb.append([KeyboardButton("🔐 Admin panel")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


# ---------------------------
# 🎵 Qo‘shiq uchun tugmalar (Tinglash / Sevimlilar / MP3)
# ---------------------------
def make_song_action_kb(youtube_url: str, title: str, artist: str = "Unknown") -> InlineKeyboardMarkup:
    safe_title = title or "Unknown"
    safe_artist = artist or "Unknown"
    payload = quote_plus(f"{safe_title}|||{safe_artist}")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("▶️ Tinglash", url=youtube_url),
            InlineKeyboardButton("❤️ Sevimlilarga", callback_data=f"fav::{payload}")
        ],
        [
            InlineKeyboardButton("📥 MP3 yuklab olish", callback_data=f"dl::{youtube_url}")
        ]
    ])
    return kb


# ---------------------------
# ⏩ Qidiruv sahifalash (Oldingi / Keyingi)
# ---------------------------
def pagination_kb(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = []
    if current_page > 0:
        buttons.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"page::{current_page - 1}"))
    if current_page < total_pages - 1:
        buttons.append(InlineKeyboardButton("➡️ Keyingi", callback_data=f"page::{current_page + 1}"))
    if not buttons:
        buttons.append(InlineKeyboardButton("🔁 Yangilash", callback_data="refresh_results"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


# ---------------------------
# 🗑 Tasdiqlovchi tugmalar
# ---------------------------
def confirm_clear_kb(action: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("✅ Ha", callback_data=f"confirm::{action}"),
            InlineKeyboardButton("❌ Yo‘q", callback_data="cancel_action")
        ]
    ])
