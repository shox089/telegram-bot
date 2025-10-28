from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile
import aiosqlite
import matplotlib.pyplot as plt
import json
import os
from utils import DB_FILE, log_error
from config import DOWNLOAD_PATH

os.makedirs(DOWNLOAD_PATH, exist_ok=True)


# ===========================
# 👤 Profilni ko‘rish
# ===========================
async def profile_command(message: types.Message):
    """
    Foydalanuvchining profil ma'lumotlarini chiqaradi:
    - Topilgan qo‘shiqlar soni
    - Eng ko‘p tinglangan ijrochi
    - Oxirgi qo‘shiq
    - Faollik
    - Janrlar diagrammasi
    """
    user_id = message.from_user.id

    try:
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute("""
                SELECT songs_found, top_artist, last_song, last_active, genres_json
                FROM users
                WHERE user_id = ?
            """, (user_id,))
            row = await cursor.fetchone()

        if not row:
            await message.answer("📊 Siz hali hech narsa qidirmagansiz.")
            return

        songs_found, top_artist, last_song, last_active, genres_json = row

        # 🔹 Matn shakli
        text = (
            f"👤 <b>Profilingiz:</b>\n\n"
            f"🎧 Topilgan qo‘shiqlar: <b>{songs_found}</b>\n"
            f"⭐ Eng ko‘p ijrochi: <b>{top_artist or '—'}</b>\n"
            f"🎵 Oxirgi qo‘shiq: <b>{last_song or '—'}</b>\n"
            f"📅 Faollik: <b>{last_active or '—'}</b>\n"
        )

        # 🔹 Janrlar diagrammasi
        genres = {}
        try:
            genres = json.loads(genres_json or "{}")
        except json.JSONDecodeError:
            pass

        chart_path = None
        if genres:
            labels = list(genres.keys())
            sizes = list(genres.values())

            fig, ax = plt.subplots(figsize=(5, 3))
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
            ax.set_title("🎶 Eng ko‘p tinglangan janrlar")
            chart_path = os.path.join(DOWNLOAD_PATH, f"{user_id}_genres.png")
            fig.tight_layout()
            fig.savefig(chart_path)
            plt.close(fig)

        # 🔹 Natijani yuborish
        if chart_path and os.path.exists(chart_path):
            await message.answer_photo(
                FSInputFile(chart_path),
                caption=text,
                parse_mode="HTML"
            )
            os.remove(chart_path)
        else:
            await message.answer(text, parse_mode="HTML")

    except Exception as e:
        log_error(f"profile_command error: {e}")
        await message.answer("❌ Profil ma'lumotlarini olishda xatolik yuz berdi.")


# ===========================
# 🔗 Handlerlarni ro‘yxatdan o‘tkazish
# ===========================
def register_handlers(dp):
    """
    Dispatcher orqali profil handlerini ro‘yxatdan o‘tkazadi
    """
    dp.message.register(profile_command, Command("profil"))
    dp.message.register(profile_command, lambda m: m.text in ["👤 Profil", "Profil"])
