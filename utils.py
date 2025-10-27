import os
import json
import re
from datetime import datetime
from config import LOG_FILE, USER_FILE, ERROR_LOG

# ---------------------------
# Bazaviy fayl yo'llari
# ---------------------------
# Agar loyihangizda ma'lumotlar bazasi fayli kerak bo'lsa
DB_FILE = "database.json"

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
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception as e:
            log_error(f"JSON load error ({path}): {e}")
            return {}

# ---------------------------
# JSON faylini saqlash
# ---------------------------
def save_json(path, data):
    """Ma'lumotni JSON fayliga yozadi"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------------------------
# Foydalanuvchi statistikasi
# ---------------------------
def update_user_stats(user_id: int, key: str, increment: int = 1):
    """Foydalanuvchi statistikasi uchun raqamni oshiradi"""
    users = load_json(USER_FILE)
    str_id = str(user_id)
    if str_id not in users:
        users[str_id] = {"stats": {}, "joined": datetime.now().isoformat()}
    if "stats" not in users[str_id]:
        users[str_id]["stats"] = {}
    if key not in users[str_id]["stats"]:
        users[str_id]["stats"][key] = 0
    users[str_id]["stats"][key] += increment
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
        yield results[i:i+page_size]

def show_results(user_id: int, page: int = 0):
    """Berilgan sahifani qaytaradi"""
    pages = list(user_pages(user_id))
    if not pages:
        return []
    if page < 0 or page >= len(pages):
        return pages[0]
    return pages[page]

# ---------------------------
# Log fayllarini yaratish
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
