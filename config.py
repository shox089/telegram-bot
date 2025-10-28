import os

# ---------------------------
# 🔐 Muhit o'zgaruvchilari
# ---------------------------
API_TOKEN = os.getenv("API_TOKEN")  # Render Environment Variables orqali
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # Agar kiritilmasa 0 bo‘ladi

# ---------------------------
# 📁 Fayllar uchun xavfsiz saqlash joylari
# ---------------------------
# Render yozishga ruxsat beradigan joy
BASE_DIR = "/opt/render/project/src"
DATA_DIR = os.path.join(BASE_DIR, "data")
DOWNLOAD_PATH = os.path.join(BASE_DIR, "downloads")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# ---------------------------
# 🗂️ Fayl yo‘llari
# ---------------------------
LOG_FILE = os.path.join(DATA_DIR, "downloads_log.json")
USER_FILE = os.path.join(DATA_DIR, "users.json")
ERROR_LOG = os.path.join(DATA_DIR, "errors.log")
DB_FILE = os.path.join(DATA_DIR, "musicbot.sqlite")
