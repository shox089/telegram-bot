from aiogram import types, F
from utils import user_search_results, update_user_stats, log_error
from keyboards import make_song_action_kb
from youtube import download_mp3_and_send


# ===========================
# 🔘 Foydalanuvchi tanlov callback
# ===========================
async def choose_callback(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id
        data_parts = callback.data.split("::")

        if len(data_parts) < 2 or not data_parts[1].isdigit():
            await callback.answer("❌ Noto‘g‘ri tanlov.")
            return

        index = int(data_parts[1]) - 1
        results = user_search_results.get(user_id, [])

        if not results or index >= len(results):
            await callback.answer("❌ Natija topilmadi.")
            return

        song = results[index]
        title = song.get("title", "Noma'lum")
        link = song.get("link")
        artist = song.get("channel") or song.get("publisher") or "Noma'lum ijrochi"

        if not link:
            await callback.answer("❌ Havola topilmadi.")
            return

        # Inline tugmalar
        kb = make_song_action_kb(link, title, artist)

        # 🎵 Qo‘shiq ma’lumotini yangilab ko‘rsatish
        await callback.message.edit_text(
            f"🎵 <b>{title}</b>\n👤 {artist}\n\n⏳ MP3 yuklanmoqda...",
            parse_mode="HTML",
            reply_markup=kb
        )

        # 🎧 MP3 yuklab yuborish
        await download_mp3_and_send(link, callback.message)

        # 📊 Foydalanuvchi statistikasi yangilanadi
        await update_user_stats(user_id, "downloads")

        await callback.answer()

    except Exception as e:
        log_error(f"choose_callback error: {e}")
        try:
            await callback.answer("❌ Xatolik yuz berdi.", show_alert=True)
        except:
            pass


# ===========================
# 🔗 Handler ro‘yxatdan o‘tkazish
# ===========================
def register_handlers(dp):
    dp.callback_query.register(choose_callback, F.data.startswith("choose::"))
