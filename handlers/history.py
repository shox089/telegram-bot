from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import load_json, save_json, log_error

LOG_FILE = "downloads_log.json"


# 📜 Tarixni ko‘rsatish
async def show_history(message: types.Message):
    try:
        user_id = str(message.from_user.id)
        logs = load_json(LOG_FILE)

        user_history = logs.get(user_id, [])
        if not user_history:
            await message.answer("📂 Sizda hali tarix mavjud emas.")
            return

        # Oxirgi 15 ta yozuvni olish
        history_list = user_history[-15:]
        text = "📂 <b>Oxirgi topilgan yoki yuklab olingan qo‘shiqlaringiz:</b>\n\n"
        for i, title in enumerate(reversed(history_list), start=1):
            text += f"{i}. {title}\n"

        clear_btn = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("🗑 Tarixni tozalash", callback_data="clear_history")]
            ]
        )

        await message.answer(text, parse_mode="HTML", reply_markup=clear_btn)

    except Exception as e:
        log_error(f"show_history error: {e}")
        await message.answer("❌ Tarixni yuklashda xatolik yuz berdi.")


# 🗑 Tarixni tozalash
async def clear_history(callback: types.CallbackQuery):
    try:
        user_id = str(callback.from_user.id)
        logs = load_json(LOG_FILE)

        if user_id in logs:
            logs[user_id] = []
            save_json(LOG_FILE, logs)

        try:
            await callback.message.edit_text("✅ Tarix muvaffaqiyatli tozalandi!")
        except:
            await callback.answer("✅ Tarix muvaffaqiyatli tozalandi!", show_alert=True)

    except Exception as e:
        log_error(f"clear_history error: {e}")
        await callback.answer("❌ Tarixni tozalashda xatolik.", show_alert=True)


# 🔗 Handlerlarni ro‘yxatdan o‘tkazish
def register_handlers(dp):
    dp.message.register(show_history, lambda m: m.text in ["📂 Tarix", "/history"])
    dp.callback_query.register(clear_history, F.data == "clear_history")
