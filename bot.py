import os
from aiogram import Bot, Dispatcher
from config import API_TOKEN

# Yuklab olishlar uchun papka
DOWNLOAD_PATH = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
