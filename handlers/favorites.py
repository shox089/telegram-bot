from aiogram import types, F
from utils import load_json, save_json, log_error
from config import DB_FILE, USER_FILE
import aiosqlite


# ❤️ Sevimlilarga qo‘shish
async def add_to_favorites(callback: types.CallbackQuery):
    try:
        # Callback formatini tekshirish
        if "::" not in callback.data:
            await callback.answer("❌ Noto‘g‘ri format.")
            return

        payload = callback.data.split("::", 1)[1]
        if "|||" not in payload:
            await callback.answer("❌ Ma’lumot yetarli emas.")
            return

        title, artist = payload.split("|||", 1)
        title, artist = title.strip(), artist.strip()
        user_id = callback.from_user.id

        # 🗃️ SQL bazaga yozish (agar jadval mavjud bo‘lmasa, yaratamiz)
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT,
                    artist TEXT,
                    UNIQUE(user_id, title)
                )
            """)
            await db.execute(
                "INSERT OR IGNORE INTO favorites (user_id, title, artist) VALUES (?, ?, ?)",
                (user_id, title, artist)
            )
            await db.commit()

        # 🧠 JSON cache yangilash (til va statistika saqlanadigan joy)
        users = load_json(USER_FILE)
        u = users.get(str(user_id), {})
        favs = u.get("favorites", [])
        if title not in favs:
            favs.append(title)
            u["favorites"] = favs
            users[str(user_id)] = u
            save_json(USER_FILE, users)

        await callback.answer("✅ Qo‘shiq sevimlilarga qo‘shildi!", show_alert=True)

    except Exception as e:
        log_error(f"add_to_favorites error: {e}")
        try:
            await callback.answer("❌ Sevimlilarga qo‘shishda xatolik.", show_alert=True)
        except:
            pass


# 📜 Sevimlilar ro‘yxatini ko‘rsatish
async def show_favorites(message: types.Message):
    try:
        user_id = message.from_user.id

        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT,
                    artist TEXT,
                    UNIQUE(user_id, title)
                )
            """)
            await db.commit()

            cur = await db.execute("""
                SELECT title, artist FROM favorites
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT 50
            """, (user_id,))
            rows = await cur.fetchall()

        if not rows:
            await message.answer("❤️ Sizda hali sevimli qo‘shiqlar yo‘q.")
            return

        text = "🎶 <b>Sevimli qo‘shiqlaringiz:</b>\n\n"
        for i, (title, artist) in enumerate(rows, start=1):
            text += f"{i}. {title} — {artist}\n"

        await message.answer(text, parse_mode="HTML")

    except Exception as e:
        log_error(f"show_favorites error: {e}")
        await message.answer("❌ Sevimlilarni ko‘rsatishda xatolik yuz berdi.")


# 🔗 Handlerlarni ro‘yxatdan o‘tkazish
def register_handlers(dp):
    dp.callback_query.register(add_to_favorites, F.data.startswith("fav::"))
    dp.message.register(show_favorites, lambda m: m.text in ["❤️ Sevimlilar", "/fav"])
