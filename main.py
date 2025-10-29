import asyncio
from bot import bot, dp
from db import init_db
from jobs import scheduler_start
from handlers import (
    start, search, choose, favorites, profile, history, admin, recommend, top_users
)
from audio import register_handlers as register_audio_handlers


# ---------------------------
# Handlerlarni ro'yxatga olish
# ---------------------------
def register_all_handlers(dp):
    """
    Barcha handlerlarni ro'yxatga oladi.
    """
    start.register_handlers(dp)
    search.register_handlers(dp)
    choose.register_handlers(dp)
    favorites.register_handlers(dp)
    profile.register_handlers(dp)
    history.register_handlers(dp)
    admin.register_handlers(dp)
    recommend.register_handlers(dp)
    top_users.register_handlers(dp)
    register_audio_handlers(dp)


# ---------------------------
# Bot ishga tushirish funksiyalari
# ---------------------------
async def on_startup():
    """
    DB, handlerlar va scheduler ishga tushiriladi.
    """
    print("🔄 DB va handlerlar ishga tushmoqda...")
    await init_db()
    register_all_handlers(dp)
    scheduler_start(bot)
    print("✅ Bot tayyor")


async def on_shutdown():
    """
    Botni to‘xtatish va sessiyalarni yopish.
    """
    await bot.session.close()
    print("🛑 Bot to‘xtadi")


# ---------------------------
# Asosiy funksiyani ishga tushirish
# ---------------------------
async def main():
    print("🤖 Bot ishga tushdi...")
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
