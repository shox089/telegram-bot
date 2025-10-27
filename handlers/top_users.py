from aiogram import types
from utils import DB_FILE
import aiosqlite

async def top_command(message: types.Message):
    async with aiosqlite.connect(DB_FILE) as db:
        cur = await db.execute("SELECT username, songs_found FROM users ORDER BY songs_found DESC LIMIT 5")
        rows = await cur.fetchall()
    if not rows:
        await message.answer("🏆 Hozircha foydalanuvchilar ro'yxati bo'sh.")
        return
    text = "🏆 <b>Eng faol foydalanuvchilar:</b>\n\n"
    for i, (username, count) in enumerate(rows, 1):
        text += f"{i}. @{username or 'NoName'} — {count} ta qo‘shiq\n"
    await message.answer(text, parse_mode="HTML")

def register_handlers(dp):
    dp.message.register(top_command, commands=["top"])
