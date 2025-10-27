from aiogram import types, F
from utils import load_json, save_json, DB_FILE, log_error
import aiosqlite

async def add_to_favorites(callback: types.CallbackQuery):
    try:
        payload = callback.data.split("::", 1)[1]
        title, artist = payload.split("|||", 1)
        user_id = callback.from_user.id

        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute(
                "INSERT OR IGNORE INTO favorites (user_id, title, artist) VALUES (?, ?, ?)",
                (user_id, title, artist)
            )
            await db.commit()

        # JSON orqali ham cache yangilash
        users = load_json("users.json")
        u = users.get(str(user_id), {})
        favs = u.get("fav", [])
        if title not in favs:
            favs.append(title)
            u["fav"] = favs
            users[str(user_id)] = u
            save_json("users.json", users)

        await callback.answer("❤️ Sevimlilarga qo‘shildi!", show_alert=True)

    except Exception as e:
        log_error(f"add_to_favorites error: {e}")
        await callback.answer("❌ Sevimlilarga qo‘shishda xatolik.", show_alert=True)

async def show_favorites(message: types.Message):
    user_id = message.from_user.id
    async with aiosqlite.connect(DB_FILE) as db:
        cur = await db.execute(
            "SELECT title, artist FROM favorites WHERE user_id=? ORDER BY id DESC LIMIT 50",
            (user_id,)
        )
        rows = await cur.fetchall()

    if not rows:
        await message.answer("❤️ Sizda hali sevimli qo‘shiqlar yo‘q.")
        return

    text = "❤️ <b>Sevimli qo‘shiqlaringiz:</b>\n\n"
    for i, (title, artist) in enumerate(rows, start=1):
        text += f"{i}. {title} — {artist}\n"

    await message.answer(text, parse_mode="HTML")

def register_handlers(dp):
    dp.callback_query.register(add_to_favorites, F.data.startswith("fav::"))
    dp.message.register(show_favorites, lambda m: m.text in ["❤️ Sevimlilar", "/fav"])
