from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import load_json, save_json, log_error
from keyboards import main_reply_keyboard
from config import ADMIN_USERNAME
import os
import json


# =======================
# 🚀 /start komandasi
# =======================
async def start_cmd(message: types.Message):
    try:
        user_id = str(message.from_user.id)
        username = message.from_user.username or ""  # Telegram username
        users_file = "users.json"

        # Fayl mavjud bo‘lmasa, yaratamiz
        if not os.path.exists(users_file):
            with open(users_file, "w", encoding="utf-8") as f:
                json.dump({}, f)

        users = load_json(users_file)

        # Yangi foydalanuvchi — til tanlash bosqichi
        if user_id not in users or "lang" not in users[user_id]:
            kb_lang = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🇺🇿 O‘zbek", callback_data="lang_uz")],
                    [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
                    [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
                ]
            )
            await message.answer("🌍 Tilni tanlang / Choose your language:", reply_markup=kb_lang)
            return

        # Eski foydalanuvchi — asosiy menyu
        kb_main = main_reply_keyboard(current_username=username)
        await message.answer("👋 Salom! Nima qilamiz?", reply_markup=kb_main)

    except Exception as e:
        log_error(f"start_cmd error: {e}")
        await message.answer("⚠️ Boshlashda xatolik yuz berdi. Iltimos, keyinroq urinib ko‘ring.")


# =======================
# 🌍 Til tanlash callback
# =======================
async def set_language(callback: types.CallbackQuery):
    try:
        lang = callback.data.split("_")[1]
        user_id = str(callback.from_user.id)
        username = callback.from_user.username or ""

        users = load_json("users.json")
        users[user_id] = users.get(user_id, {})
        users[user_id]["lang"] = lang
        save_json("users.json", users)

        # Asosiy menyuga qaytamiz
        kb_main = main_reply_keyboard(current_username=username)
        await callback.message.edit_text("✅ Til saqlandi! Endi asosiy menyuga qayting.")
        await callback.message.answer("👋 Salom! Nima qilamiz?", reply_markup=kb_main)
        await callback.answer()

    except Exception as e:
        log_error(f"set_language error: {e}")
        await callback.answer("❌ Tilni saqlashda xatolik yuz berdi.", show_alert=True)


# =======================
# 🔗 Handlerlarni ro‘yxatdan o‘tkazish
# =======================
def register_handlers(dp):
    dp.message.register(start_cmd, Command("start"))
    dp.callback_query.register(set_language, F.data.startswith("lang_"))
