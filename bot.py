import os
from aiogram import Bot, Dispatcher
from config import API_TOKEN, DOWNLOAD_PATH as CONFIG_DOWNLOAD_PATH

# ---------------------------
# 📁 Yuklab olishlar uchun papka
# ---------------------------
DOWNLOAD_PATH = CONFIG_DOWNLOAD_PATH
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# ---------------------------
# 🤖 Bot va Dispatcher
# ---------------------------
bot = Bot(
    token=API_TOKEN,
    default={"parse_mode": "HTML"}  # ✅ faqat lug‘at tarzida
)
dp = Dispatcher()
