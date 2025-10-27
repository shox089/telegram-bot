from aiogram import types, F
from utils import load_json, save_json

LOG_FILE = "downloads_log.json"

async def show_history(message: types.Message):
    user_id = str(message.from_user.id)
    logs = load_json(LOG_FILE)
    if user_id not in logs or not logs[user_id]:
        await message.answer("📂 Sizda hali tarix mavjud emas.")
        return
    history_list = logs[user_id][-15:]
    text = "📂 <b>Oxirgi topilgan yoki yuklab olingan qo‘shiqlaringiz:</b>\n\n"
    for i, title in enumerate(reversed(history_list), 1):
        text += f"{i}. {title}\n"
    clear_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("🗑 Tarixni tozalash", callback_data="clear_history")]])
    await message.answer(text, parse_mode="HTML", reply_markup=clear_btn)

async def clear_history(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    logs = load_json(LOG_FILE)
    if user_id in logs:
        logs[user_id] = []
        save_json(LOG_FILE, logs)
    try:
        await callback.message.edit_text("✅ Tarix muvaffaqiyatli tozalandi!")
    except:
        await callback.answer("✅ Tarix muvaffaqiyatli tozalandi!", show_alert=True)

def register_handlers(dp):
    dp.message.register(show_history, lambda m: m.text in ["📂 Tarix / History"])
    dp.callback_query.register(clear_history, F.data=="clear_history")
