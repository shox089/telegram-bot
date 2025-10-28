import os
from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import load_json, ERROR_LOG

ADMIN_ID = 6688725338


# 🔐 Admin panelni ochish
async def handle_admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Bu bo‘lim faqat admin uchun.")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="🎧 Oxirgi yuklamalar", callback_data="admin_downloads")],
        [InlineKeyboardButton(text="⚠️ Xatoliklar", callback_data="admin_errors")]
    ])
    await message.answer("🔐 <b>Admin panelga xush kelibsiz:</b>", parse_mode="HTML", reply_markup=kb)


# 🔘 Admin tugmalari orqali ishlovchi callbacklar
async def admin_buttons(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Bu bo‘lim faqat admin uchun.", show_alert=True)
        return

    data = callback.data

    # 📊 Statistika
    if data == "admin_stats":
        users = load_json("users.json")
        logs = load_json("downloads_log.json")
        total_users = len(users)
        total_downloads = sum(len(v) for v in logs.values())
        avg_downloads = total_downloads / total_users if total_users else 0
        text = (
            f"📊 <b>Statistika:</b>\n\n"
            f"👤 Foydalanuvchilar: <b>{total_users}</b>\n"
            f"🎧 Yuklab olishlar: <b>{total_downloads}</b>\n"
            f"📈 O‘rtacha yuklamalar: <b>{avg_downloads:.1f}</b>"
        )
        await callback.message.edit_text(text, parse_mode="HTML")

    # 🎧 Oxirgi yuklamalar
    elif data == "admin_downloads":
        logs = load_json("downloads_log.json")
        all_songs = [song for user_songs in logs.values() for song in user_songs]
        last_songs = all_songs[-10:] if all_songs else []

        if not last_songs:
            await callback.message.edit_text("📂 Hozircha hech narsa yuklab olinmagan.")
            return

        text = "🎶 <b>So‘nggi 10 ta yuklab olingan qo‘shiqlar:</b>\n\n"
        text += "\n".join(f"{i}. {song}" for i, song in enumerate(last_songs, 1))
        await callback.message.edit_text(text, parse_mode="HTML")

    # ⚠️ Xatoliklar
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


# 🔗 Handlerlarni ro‘yxatdan o‘tkazish
def register_handlers(dp):
    dp.message.register(handle_admin_panel, F.text == "🔐 Admin panel")
    dp.callback_query.register(admin_buttons, F.data.startswith("admin_"))
