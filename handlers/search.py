from aiogram import types, F
from youtube import search_youtube
from utils import user_search_results, user_pages, show_results, log_error


# =======================
# 🔍 Matn orqali qidiruv
# =======================
async def text_search(message: types.Message):
    # Agar matn yo'q bo‘lsa (masalan, foydalanuvchi rasm, ovoz yoki fayl yuborsa) — e’tibor bermaymiz
    if not message.text:
        return

    query = message.text.strip()

    # Buyruqlarni inkor etamiz (masalan /start, /help)
    if not query or query.startswith("/"):
        return

    try:
        status_msg = await message.answer(f"🔎 Qidirilmoqda: <b>{query}</b>", parse_mode="HTML")

        # YouTube'dan natijalar olish
        results = await search_youtube(query, limit=20)

        if not results:
            await status_msg.edit_text("❌ YouTube’da hech narsa topilmadi.")
            return

        # Foydalanuvchi uchun natijalarni saqlash
        user_search_results[message.from_user.id] = results
        user_pages[message.from_user.id] = 0

        # Natijalarni ko‘rsatish
        await show_results(message.from_user.id, status_msg)

    except Exception as e:
        log_error(f"text_search error: {e}")
        await message.answer("❌ Qidiruvda xatolik yuz berdi.")


# =======================
# ⏩ Sahifani almashtirish
# =======================
async def change_page(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    try:
        # Sahifani o‘zgartirish
        if callback.data == "next_page":
            user_pages[user_id] = user_pages.get(user_id, 0) + 1
        elif callback.data == "prev_page":
            user_pages[user_id] = max(0, user_pages.get(user_id, 0) - 1)

        await show_results(user_id, callback.message)
        await callback.answer()

    except Exception as e:
        log_error(f"change_page error: {e}")
        await callback.answer("⚠️ Sahifani o‘zgartirishda xatolik.", show_alert=True)


# =======================
# 🔗 Handlerlarni ro‘yxatdan o‘tkazish
# =======================
def register_handlers(dp):
    # Faqat matnli xabarlarni ushlash (media emas)
    dp.message.register(text_search, F.text)

    # Inline tugmalar uchun
    dp.callback_query.register(change_page, F.data.in_(["next_page", "prev_page"]))
