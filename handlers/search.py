from aiogram import types, F
from youtube import search_youtube
from utils import user_search_results, show_results, log_error
from keyboards import make_song_action_kb, pagination_kb
from config import RESULTS_PER_PAGE

# ===========================
# 🔍 YouTube qidiruv handler
# ===========================
async def text_search(message: types.Message):
    """
    Foydalanuvchi matn yuborganda YouTube'da qidiruv amalga oshiradi.
    """
    if not message.text or message.text.startswith("/"):
        return

    query = message.text.strip()
    status_msg = await message.answer(f"🔎 Qidirilmoqda: <b>{query}</b>", parse_mode="HTML")

    try:
        results = await search_youtube(query, limit=30)
        if not results:
            await status_msg.edit_text("❌ Hech narsa topilmadi.")
            return

        # Foydalanuvchi natijalarini saqlash
        user_search_results[message.from_user.id] = results

        # Birinchi sahifani ko‘rsatamiz
        await show_results_page(message, user_id=message.from_user.id, page=0)

    except Exception as e:
        log_error(f"text_search error: {e}")
        await message.answer("⚠️ Qidiruvda xatolik yuz berdi.")


# ===========================
# 📄 Sahifa ko‘rsatish funksiyasi
# ===========================
async def show_results_page(message_or_callback, user_id: int, page: int):
    """
    Berilgan foydalanuvchi uchun sahifalangan qidiruv natijalarini ko‘rsatadi.
    """
    results = user_search_results.get(user_id, [])
    if not results:
        await message_or_callback.answer("❌ Natijalar topilmadi.")
        return

    total_pages = (len(results) + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
    start = page * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    items = results[start:end]

    # Har bir video uchun alohida xabar
    text_lines = [f"<b>Sahifa {page+1}/{total_pages}</b>\n"]
    for idx, item in enumerate(items, start=start + 1):
        text_lines.append(
            f"🎵 <b>{item['title']}</b>\n"
            f"⏱ {item['duration']} | 👁 {item['views']} | 📅 {item['published']}\n"
            f"🔗 {item['link']}\n"
        )

    text = "\n".join(text_lines)

    # Pagination tugmalari
    keyboard = pagination_kb(page, total_pages)

    if isinstance(message_or_callback, types.Message):
        await message_or_callback.answer(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message_or_callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)


# ===========================
# ⏩ Sahifa almashtirish handler
# ===========================
async def change_page(callback: types.CallbackQuery):
    """
    Callback orqali sahifani almashtirish.
    """
    try:
        _, page_str = callback.data.split("::")
        page = int(page_str)
        await show_results_page(callback, user_id=callback.from_user.id, page=page)
        await callback.answer()
    except Exception as e:
        log_error(f"change_page error: {e}")
        await callback.answer("⚠️ Sahifani almashtirishda xatolik.", show_alert=True)


# ===========================
# 🔗 Handlerlarni ro‘yxatdan o‘tkazish
# ===========================
def register_handlers(dp):
    dp.message.register(text_search, F.text)
    dp.callback_query.register(change_page, F.data.startswith("page::"))
