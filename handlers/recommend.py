from aiogram import types
from utils import search_youtube, DB_FILE
import aiosqlite

async def recommend_command(message: types.Message):
    user_id = message.from_user.id
    async with aiosqlite.connect(DB_FILE) as db:
        cur = await db.execute("SELECT top_artist FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
    if not row or not row[0]:
        await message.answer("🧠 Siz uchun hali tavsiyalar yo'q. Avval bir nechta qo'shiq toping.")
        return
    top_artist = row[0]
    results = await search_youtube(f"{top_artist} top hits", limit=5)
    if not results:
        await message.answer("🧠 Tavsiya topilmadi.")
        return
    text = f"🧠 <b>{top_artist}</b> ijrochisidan tavsiya:\n\n"
    for i, r in enumerate(results, 1):
        text += f"{i}. {r['title']}\n"
    await message.answer(text, parse_mode="HTML")

def register_handlers(dp):
    dp.message.register(recommend_command, commands=["tavsiya"])
