from aiogram import types
from aiogram.filters import Command
from youtube import search_youtube
from utils import DB_FILE, log_error
import aiosqlite


# =======================
# 🧠 Tavsiya berish
# =======================
async def recommend_command(message: types.Message):
    user_id = message.from_user.id

    try:
        # Eng ko‘p tinglangan ijrochini olish
        async with aiosqlite.connect(DB_FILE) as db:
            cur = await db.execute(
                "SELECT top_artist FROM users WHERE user_id = ?",
                (user_id,)
            )
            row = await cur.fetchone()

        if not row or not row[0]:
            await message.answer("🧠 Siz uchun hali tavsiyalar yo‘q. Avval bir nechta qo‘shiq qidiring.")
            return

        top_artist = row[0]

        # YouTube’dan tavsiyalar olish
        results = await search_youtube(f"{top_artist} top hits", limit=5)
        if not results:
            await message.answer("😕 Tavsiya topilmadi.")
            return

        # Natijani shakllantirish
        text = f"🧠 <b>{top_artist}</b> ijrochisidan tavsiya qilinadigan qo‘shiqlar:\n\n"
        for i, r in enumerate(results, 1):
            text += f"{i}. {r['title']}\n"

        await message.answer(text, parse_mode="HTML")

    except Exception as e:
        log_error(f"recommend_command error: {e}")
        await message.answer("❌ Tavsiyalarni olishda xatolik yuz berdi.")


# =======================
# 🔗 Handler ro‘yxatdan o‘tkazish
# =======================
def register_handlers(dp):
    dp.message.register(recommend_command, Command("tavsiya"))
    dp.message.register(recommend_command, lambda m: m.text in ["🧠 Tavsiya", "Tavsiya"])
