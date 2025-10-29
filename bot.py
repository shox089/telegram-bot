import os
from aiogram import Bot, Dispatcher
from config import API_TOKEN, DOWNLOAD_PATH as CONFIG_DOWNLOAD_PATH

# ---------------------------
# 📁 Yuklab olishlar uchun papka
# ---------------------------
DOWNLOAD_PATH = CONFIG_DOWNLOAD_PATH  # config.py da aniqlangan papka
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# ---------------------------
# 🤖 Bot va Dispatcher
# ---------------------------
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher()
