from aiogram import types
from aiogram.filters import Command
from utils import DB_FILE, log_error
import aiosqlite

# =======================
# 🏆 Eng faol foydalanuvchilar komandasi
# =======================
async def top_command(message: types.Message):
    """
    Top 5 eng faol foydalanuvchilarni ko‘rsatadi
    (songs_found bo‘yicha tartiblangan)
    """
    try:
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                "SELECT username, songs_found FROM users ORDER BY songs_found DESC LIMIT 5"
            )
            rows = await cursor.fetchall()

        if not rows:
            await message.answer("🏆 Hozircha foydalanuvchilar ro‘yxati bo‘sh.")
            return

        text = "🏆 <b>Eng faol foydalanuvchilar:</b>\n\n"
        for i, (username, count) in enumerate(rows, start=1):
            display_name = f"@{username}" if username else "Anonim foydalanuvchi"
            text += f"{i}. {display_name} — <b>{count}</b> ta qo‘shiq\n"

        await message.answer(text, parse_mode="HTML")

    except Exception as e:
        log_error(f"top_command error: {e}")
        await message.answer("❌ Xatolik yuz berdi, keyinroq urinib ko‘ring.")


# =======================
# 🔗 Handler ro‘yxatdan o‘tkazish
# =======================
def register_handlers(dp):
    dp.message.register(top_command, Command("top"))
