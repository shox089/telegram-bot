import os
from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import load_json, ERROR_LOG

ADMIN_ID = 6688725338

async def handle_admin_panel(message: types.Message):
    if message.text != "🔐 Admin panel" or message.from_user.id != ADMIN_ID:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("🎧 Oxirgi yuklamalar", callback_data="admin_downloads")],
        [InlineKeyboardButton("⚠️ Xatoliklar", callback_data="admin_errors")]
    ])
    await message.answer("🔐 Admin panelga xush kelibsiz:", reply_markup=kb)

async def admin_buttons(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Bu bo‘lim faqat admin uchun.", show_alert=True)
        return

    data = callback.data

    if data == "admin_stats":
        users = load_json("users.json")
        logs = load_json("downloads_log.json")
        total_users = len(users)
        total_downloads = sum(len(v) for v in logs.values())
        text = (f"📊 <b>Statistika:</b>\n\n👤 Foydalanuvchilar: <b>{total_users}</b>\n"
                f"🎧 Yuklab olishlar: <b>{total_downloads}</b>\n"
                f"🗓️ O‘rtacha yuklamalar: {total_downloads / total_users if total_users else 0:.1f}")
        await callback.message.edit_text(text, parse_mode="HTML")

    elif data == "admin_downloads":
        logs = load_json("downloads_log.json")
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
            errors = f.readlines()[-20:]
        if not errors:
            await callback.message.edit_text("✅ Hozircha xatoliklar yo‘q.")
            return
        text = "⚠️ <b>So‘nggi xatoliklar:</b>\n\n" + "".join(errors)
        await callback.message.edit_text(text, parse_mode="HTML")

    await callback.answer()

def register_handlers(dp):
    dp.message.register(handle_admin_panel, lambda m: m.text=="🔐 Admin panel")
    dp.callback_query.register(admin_buttons, F.data.startswith("admin_"))
