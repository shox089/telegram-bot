from aiogram import types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from utils import DB_FILE, log_error
import aiosqlite
import matplotlib.pyplot as plt
import json
import os

# =======================
# 👤 Profilni ko‘rish
# =======================
async def profile_command(message: types.Message):
    user_id = message.from_user.id

    try:
        # Ma'lumotlarni olish
        async with aiosqlite.connect(DB_FILE) as db:
            cur = await db.execute(
                """
                SELECT songs_found, top_artist, last_song, last_active, genres_json
                FROM users
                WHERE user_id = ?
                """,
                (user_id,)
            )
            row = await cur.fetchone()

        if not row:
            await message.answer("📊 Siz hali hech narsa qidirmagansiz.")
            return

        songs_found, top_artist, last_song, last_active, genres_json = row
        text = (
            f"👤 <b>Profilingiz:</b>\n\n"
            f"🎧 Topilgan qo‘shiqlar: <b>{songs_found}</b>\n"
            f"⭐ Eng ko‘p ijrochi: <b>{top_artist or '—'}</b>\n"
            f"🎵 Oxirgi qo‘shiq: <b>{last_song or '—'}</b>\n"
            f"📅 Faollik: <b>{last_active or '—'}</b>\n"
        )

        # Janrlar bo‘yicha diagramma
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
            chart_path = f"downloads/{user_id}_genres.png"
            fig.tight_layout()
            fig.savefig(chart_path)
            plt.close(fig)

        # Natijani yuborish
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


# =======================
# 🔗 Handler ro‘yxatdan o‘tkazish
# =======================
def register_handlers(dp):
    # Foydalanuvchi /profil yoki 👤 Profil tugmasi yuborganda ishlaydi
    dp.message.register(profile_command, Command("profil"))
    dp.message.register(profile_command, lambda m: m.text in ["👤 Profil", "Profil"])
