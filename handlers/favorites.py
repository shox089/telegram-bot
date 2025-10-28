from aiogram import types, F
import aiosqlite
from utils import load_json, save_json, log_error
from config import DB_FILE, USER_FILE


# ===========================
# ❤️ Sevimlilarga qo‘shish
# ===========================
async def add_to_favorites(callback: types.CallbackQuery):
    """
    Callback orqali qo‘shiqni foydalanuvchining sevimlilari ro‘yxatiga qo‘shadi.
    """
    try:
        # 🔹 Callback formatini tekshirish
        if "::" not in callback.data:
            await callback.answer("❌ Noto‘g‘ri format.")
            return

        payload = callback.data.split("::", 1)[1]
        if "|||" not in payload:
            await callback.answer("❌ Ma’lumot yetarli emas.")
            return

        title, artist = [x.strip() for x in payload.split("|||", 1)]
        user_id = callback.from_user.id

        # 🗃️ SQL bazada jadvalni yaratish (agar mavjud bo‘lmasa)
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
            await db.execute("""
                INSERT OR IGNORE INTO favorites (user_id, title, artist)
                VALUES (?, ?, ?)
            """, (user_id, title, artist))
            await db.commit()

        # 🧠 JSON cache yangilash (foydalanuvchi ma’lumotlari uchun)
        users = load_json(USER_FILE)
        u = users.get(str(user_id), {})
        favorites = u.get("favorites", [])
        if title not in favorites:
            favorites.append(title)
            u["favorites"] = favorites
            users[str(user_id)] = u
            save_json(USER_FILE, users)

        await callback.answer("✅ Qo‘shiq sevimlilarga qo‘shildi!", show_alert=True)

    except Exception as e:
        log_error(f"add_to_favorites error: {e}")
        try:
            await callback.answer("❌ Sevimlilarga qo‘shishda xatolik yuz berdi.", show_alert=True)
        except:
            pass


# ===========================
# 📜 Sevimlilar ro‘yxatini ko‘rsatish
# ===========================
async def show_favorites(message: types.Message):
    """
    Foydalanuvchining sevimli qo‘shiqlari ro‘yxatini chiqaradi.
    """
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

            cursor = await db.execute("""
                SELECT title, artist FROM favorites
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT 50
            """, (user_id,))
            rows = await cursor.fetchall()

        # 🔹 Sevimlilar bo‘sh bo‘lsa
        if not rows:
            await message.answer("❤️ Sizda hali sevimli qo‘shiqlar yo‘q.")
            return

        # 🔹 Ro‘yxat shakllantirish
        text_lines = [f"{i}. {title} — {artist}" for i, (title, artist) in enumerate(rows, start=1)]
        text = "🎶 <b>Sevimli qo‘shiqlaringiz:</b>\n\n" + "\n".join(text_lines)

        await message.answer(text, parse_mode="HTML")

    except Exception as e:
        log_error(f"show_favorites error: {e}")
        await message.answer("❌ Sevimlilarni ko‘rsatishda xatolik yuz berdi.")


# ===========================
# 🔗 Handlerlarni ro‘yxatdan o‘tkazish
# ===========================
def register_handlers(dp):
    """
    Dispatcher orqali handlerlarni ro‘yxatdan o‘tkazadi.
    """
    dp.callback_query.register(add_to_favorites, F.data.startswith("fav::"))
    dp.message.register(show_favorites, lambda m: m.text in ["❤️ Sevimlilar", "/fav"])
