import asyncio
from aiogram import Bot, Dispatcher
from config import API_TOKEN
from db import init_db
from jobs import scheduler_start
from handlers import start, search, choose, favorites, profile, history, admin, recommend, top_users
from audio import audio_handlers

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def on_startup():
    await init_db()
    scheduler_start(bot)

async def main():
    print("🤖 Bot ishga tushdi...")
    await on_startup()
    # handlers import qilinishi bilan avtomatik ro‘yxatga olinadi
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
