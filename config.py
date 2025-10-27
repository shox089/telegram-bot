import os

API_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 6688725338

DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

LOG_FILE = "downloads_log.json"
USER_FILE = "users.json"
ERROR_LOG = "errors.log"
DB_FILE = "musicbot.sqlite"
