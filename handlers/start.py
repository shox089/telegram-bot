from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import load_json, save_json
from keyboards import main_reply_keyboard
from config import ADMIN_ID

async def start_cmd(message: types.Message, dp=None):
    users = load_json("users.json")
    user_id = str(message.from_user.id)
    if user_id not in users:
        kb_lang = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇿 O‘zbek", callback_data="lang_uz")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
        ])
        await message.answer("🌍 Tilni tanlang / Choose language:", reply_markup=kb_lang)
    else:
        kb_main = main_reply_keyboard(message.from_user.id == ADMIN_ID)
        await message.answer("👋 Salom! Nima qilamiz?", reply_markup=kb_main)

async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    users = load_json("users.json")
    users[str(callback.from_user.id)] = users.get(str(callback.from_user.id), {})
    users[str(callback.from_user.id)]["lang"] = lang
    save_json("users.json", users)
    await callback.message.edit_text("✅ Til saqlandi! Endi asosiy menyuga qayting.")

def register_handlers(dp):
    dp.message.register(start_cmd, Command("start"))
    dp.callback_query.register(set_language, F.data.startswith("lang_"))
