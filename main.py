import asyncio
from aiogram import Bot, Dispatcher
from config import API_TOKEN
from db import init_db
from handlers import register_handlers

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def on_startup():
    await init_db()
    register_handlers(dp)

async def main():
    print("🤖 Bot ishga tushdi...")
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
