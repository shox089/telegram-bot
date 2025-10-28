from aiogram import types, F
from utils import (
    user_search_results,
    update_user_stats,
    log_error
)
from keyboards import make_song_action_kb
from youtube import download_mp3_and_send


# 🔘 Foydalanuvchi tanloviga ishlov berish
async def choose_callback(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id
        data_parts = callback.data.split("::")

        if len(data_parts) < 2 or not data_parts[1].isdigit():
            await callback.answer("❌ Noto‘g‘ri tanlov.")
            return

        index = int(data_parts[1]) - 1
        results = user_search_results(user_id)

        if not results or index >= len(results):
            await callback.answer("❌ Natija topilmadi.")
            return

        song = results[index]
        title = song.get("title", "Unknown")
        link = song.get("link")
        artist = song.get("channel", "Unknown artist")

        kb = make_song_action_kb(link, title, artist)

        # 🎵 Qo‘shiq nomini ko‘rsatish
        await callback.message.edit_text(
            f"🎵 <b>{title}</b>\n👤 {artist}",
            parse_mode="HTML",
            reply_markup=kb
        )

        # 🎧 MP3 ni yuklab yuborish
        await download_mp3_and_send(link, callback.message)

        # 📊 Foydalanuvchi statistikasi yangilanadi
        update_user_stats(user_id, "downloads")

        await callback.answer()

    except Exception as e:
        log_error(f"choose_callback error: {e}")
        try:
            await callback.answer("❌ Xatolik yuz berdi.", show_alert=True)
        except:
            pass


# 🔗 Handlerni ro‘yxatdan o‘tkazish
def register_handlers(dp):
    dp.callback_query.register(choose_callback, F.data.startswith("choose::"))
