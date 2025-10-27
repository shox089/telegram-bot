import os

API_TOKEN = os.getenv("API_TOKEN")      # Renderdan oladi
ADMIN_ID = os.getenv("ADMIN_ID")  # str bo'ladi, username sifatida ishlatish mumkin
DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

LOG_FILE = "downloads_log.json"
USER_FILE = "users.json"
ERROR_LOG = "errors.log"
DB_FILE = "musicbot.sqlite"
