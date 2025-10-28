import os
import json
import re
from datetime import datetime

# ---------------------------
# Ma'lumotlar uchun xavfsiz papka
# ---------------------------
DATA_DIR = "/opt/render/project/src/data"
os.makedirs(DATA_DIR, exist_ok=True)

# Fayl nomlari
DB_FILE = os.path.join(DATA_DIR, "database.json")
LOG_FILE = os.path.join(DATA_DIR, "downloads.json")
USER_FILE = os.path.join(DATA_DIR, "users.json")
ERROR_LOG = os.path.join(DATA_DIR, "errors.log")

# ---------------------------
# Xatoliklarni log qilish
# ---------------------------
def log_error(msg: str):
    """Xatoliklarni ERROR_LOG fayliga yozadi"""
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

# ---------------------------
# Fayl nomini tozalash
# ---------------------------
def clean_filename(name: str) -> str:
    """Fayl nomida ruxsat etilmagan belgilarni olib tashlaydi"""
    return re.sub(r'[\\/*?:"<>|]', "", name) if name else "unknown"

# ---------------------------
# JSON faylini yuklash
# ---------------------------
def load_json(path):
    """JSON faylini yuklaydi, xatolik bo'lsa bo'sh lug'at qaytaradi"""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log_error(f"JSON load error ({path}): {e}")
        return {}

# ---------------------------
# JSON faylini saqlash
# ---------------------------
def save_json(path, data):
    """Ma'lumotni JSON fayliga yozadi"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_error(f"JSON save error ({path}): {e}")

# ---------------------------
# Foydalanuvchi statistikasi
# ---------------------------
def update_user_stats(user_id: int, key: str, increment: int = 1):
    """Foydalanuvchi statistikasi uchun raqamni oshiradi"""
    users = load_json(USER_FILE)
    str_id = str(user_id)
    if str_id not in users:
        users[str_id] = {"stats": {}, "joined": datetime.now().isoformat()}
    users[str_id]["stats"][key] = users[str_id]["stats"].get(key, 0) + increment
    save_json(USER_FILE, users)

# ---------------------------
# YouTube qidiruv natijalarini saqlash va sahifalash
# ---------------------------
user_search_results_data = {}

def user_search_results(user_id: int):
    """Foydalanuvchining qidiruv natijalarini qaytaradi"""
    return user_search_results_data.get(user_id, [])

def user_pages(user_id: int, page_size: int = 5):
    """Natijalarni sahifalash uchun generator"""
    results = user_search_results(user_id)
    for i in range(0, len(results), page_size):
        yield results[i:i + page_size]

def show_results(user_id: int, page: int = 0):
    """Berilgan sahifani qaytaradi"""
    pages = list(user_pages(user_id))
    if not pages:
        return []
    if page < 0 or page >= len(pages):
        return pages[0]
    return pages[page]

# ---------------------------
# Fayllarni yaratish
# ---------------------------
for file in [LOG_FILE, USER_FILE, DB_FILE]:
    if not os.path.exists(file):
        save_json(file, {})

# ---------------------------
# Yuklashlarni log qilish
# ---------------------------
def log_download(user_id: int, item: dict):
    """Yuklashlarni log qiladi"""
    logs = load_json(LOG_FILE)
    str_id = str(user_id)
    if str_id not in logs:
        logs[str_id] = []
    logs[str_id].append({
        "time": datetime.now().isoformat(),
        "item": item
    })
    save_json(LOG_FILE, logs)
