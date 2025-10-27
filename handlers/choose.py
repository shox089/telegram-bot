from aiogram import types, F
from utils import user_search_results, user_pages, update_user_stats, log_error, clean_filename, load_json, save_json
from keyboards import make_song_action_kb
from youtube import download_mp3_and_send

async def choose_callback(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id
        index = int(callback.data.split("::")[1]) - 1
        results = user_search_results.get(user_id)
        if not results or index >= len(results):
            await callback.answer("❌ Topilmadi.")
            return
        song = results[index]
        title = song.get("title")
        link = song.get("link")
        kb = make_song_action_kb(link, title, "Unknown")
        await callback.message.edit_text(f"🎵 <b>{title}</b>", parse_mode="HTML", reply_markup=kb)
        await download_mp3_and_send(user_id, title, link, callback.message)
    except Exception as e:
        log_error(f"choose_callback error: {e}")
        await callback.answer("❌ Xatolik yuz berdi.")

def register_handlers(dp):
    dp.callback_query.register(choose_callback, F.data.startswith("choose::"))
