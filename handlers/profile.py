from aiogram import types
from aiogram.types import FSInputFile
from utils import DB_FILE
import aiosqlite
import matplotlib.pyplot as plt
import json
import os

async def profile_command(message: types.Message):
    user_id = message.from_user.id
    async with aiosqlite.connect(DB_FILE) as db:
        cur = await db.execute(
            "SELECT songs_found, top_artist, last_song, last_active, genres_json FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()

    if not row:
        await message.answer("📊 Siz hali hech narsa qidirmagansiz.")
        return

    songs_found, top_artist, last_song, last_active, genres_json = row
    text = (f"👤 <b>Profil:</b>\n\n"
            f"🎧 Topilgan qo‘shiqlar: <b>{songs_found}</b>\n"
            f"⭐ Eng ko‘p ijrochi: <b>{top_artist or '—'}</b>\n"
            f"🎵 Oxirgi qo‘shiq: <b>{last_song or '—'}</b>\n"
            f"📅 Faollik: <b>{last_active or '—'}</b>\n")

    try:
        genres = json.loads(genres_json or "{}")
    except:
        genres = {}

    chart_path = None
    if genres:
        labels = list(genres.keys())
        sizes = list(genres.values())
        fig, ax = plt.subplots(figsize=(5,3))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title("Eng ko'p tinglangan janrlar")
        chart_path = f"downloads/{user_id}_genres.png"
        fig.tight_layout()
        fig.savefig(chart_path)
        plt.close(fig)

    if chart_path and os.path.exists(chart_path):
        await message.answer_photo(FSInputFile(chart_path), caption=text, parse_mode="HTML")
        os.remove(chart_path)
    else:
        await message.answer(text, parse_mode="HTML")

def register_handlers(dp):
    dp.message.register(profile_command, commands=["profil"])
