import asyncio
from bot import bot, dp  # 🔹 bot.py faylidan tayyor bot va dp ni import qilamiz
from db import init_db
from jobs import scheduler_start
from handlers import (
    start, search, choose, favorites, profile, history, admin, recommend, top_users
)
from audio import register_handlers as register_audio_handlers  # ✅ audio handlerlari


# ---------------------------
# Handlerlarni ro'yxatga olish
# ---------------------------
def register_all_handlers(dp):
    start.register_handlers(dp)
    search.register_handlers(dp)
    choose.register_handlers(dp)
    favorites.register_handlers(dp)
    profile.register_handlers(dp)
    history.register_handlers(dp)
    admin.register_handlers(dp)
    recommend.register_handlers(dp)
    top_users.register_handlers(dp)
    register_audio_handlers(dp)  # ✅ audio handlerlar endi to‘g‘ri chaqiriladi


# ---------------------------
# Bot ishga tushirish funksiyalari
# ---------------------------
async def on_startup():
    await init_db()  # ✅ DB ni ishga tushirish
    register_all_handlers(dp)  # ✅ Handlerlarni ro'yxatga olish
    scheduler_start(bot)  # ✅ Scheduler ishga tushadi


async def main():
    print("🤖 Bot ishga tushdi...")
    await on_startup()
    await dp.start_polling(bot)  # ✅ Pollingni boshlash


if __name__ == "__main__":
    asyncio.run(main())
