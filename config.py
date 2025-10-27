import os

API_TOKEN = os.getenv("API_TOKEN")      # Renderdan oladi
ADMIN_ID = int(os.getenv("ADMIN_ID"))   # Renderdan oladi

DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

LOG_FILE = "downloads_log.json"
USER_FILE = "users.json"
ERROR_LOG = "errors.log"
DB_FILE = "musicbot.sqlite"
