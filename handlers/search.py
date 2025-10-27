from aiogram import types, F
from utils import user_search_results, user_pages, show_results
from keyboards import make_song_action_kb
from youtube import search_youtube

async def text_search(message: types.Message):
    query = message.text.strip()
    if query.startswith("/"):
        return
    status_msg = await message.answer(f"🔎 Qidirilmoqda: {query}")
    results = await search_youtube(query, limit=20)
    if not results:
        await status_msg.edit_text("❌ YouTube natija topilmadi.")
        return
    user_search_results[message.from_user.id] = results
    user_pages[message.from_user.id] = 0
    await show_results(message.from_user.id, status_msg)

async def change_page(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if callback.data == "next_page":
        user_pages[user_id] = user_pages.get(user_id, 0) + 1
    elif callback.data == "prev_page":
        user_pages[user_id] = max(0, user_pages.get(user_id, 0) - 1)
    await show_results(user_id, callback.message)
    await callback.answer()

def register_handlers(dp):
    dp.message.register(text_search)
    dp.callback_query.register(change_page, F.data.in_(["next_page", "prev_page"]))
