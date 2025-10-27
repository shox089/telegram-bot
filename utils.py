import os
import json
import re
from datetime import datetime
from config import LOG_FILE, USER_FILE, ERROR_LOG, DOWNLOAD_PATH

# ---------------------------
# Log va Error funksiyalari
# ---------------------------
def log_error(msg: str):
    """Xatoliklarni log faylga yozadi"""
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def log_download(user_id: int, filename: str):
    """Foydalanuvchi yuklagan fayllarni loglash"""
    data = load_json(LOG_FILE)
    if str(user_id) not in data:
        data[str(user_id)] = []
    data[str(user_id)].append({
        "file": filename,
        "time": datetime.now().isoformat()
    })
    save_json(LOG_FILE, data)

# ---------------------------
# JSON fayllarni boshqarish
# ---------------------------
def load_json(path):
    """JSON faylni yuklash"""
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception as e:
            log_error(f"load_json error ({path}): {e}")
            return {}

def save_json(path, data):
    """JSON faylni saqlash"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------------------------
# Foydalanuvchi fayllari
# ---------------------------
def add_user(user_id: int, username: str = None):
    """Foydalanuvchini users.json ga qo'shish"""
    users = load_json(USER_FILE)
    if str(user_id) not in users:
        users[str(user_id)] = {
            "username": username,
            "joined": datetime.now().isoformat()
        }
        save_json(USER_FILE, users)

# ---------------------------
# Fayl nomini tozalash
# ---------------------------
def clean_filename(name: str) -> str:
    """Fayl nomidagi noqonuniy belgilarni olib tashlaydi"""
    return re.sub(r'[\\/*?:"<>|]', "", name) if name else "unknown"

# ---------------------------
# Qidiruv va natijalarni boshqarish
# ---------------------------
def user_search_results(query: str, data: list) -> list:
    """Data ichidan query bo‘yicha mos keladigan natijalarni topadi"""
    return [item for item in data if query.lower() in item.lower()]

def user_pages(results: list, page: int = 1, per_page: int = 5) -> list:
    """Natijalarni sahifalash"""
    start = (page - 1) * per_page
    end = start + per_page
    return results[start:end]

def show_results(results: list) -> str:
    """Natijalarni string ko‘rinishida formatlash"""
    if not results:
        return "Natija topilmadi."
    return "\n".join(results)

# ---------------------------
# Download papkasini yaratish
# ---------------------------
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# ---------------------------
# Log fayllarni yaratish
# ---------------------------
for file in [LOG_FILE, USER_FILE, ERROR_LOG]:
    if not os.path.exists(file):
        if file.endswith(".json"):
            save_json(file, {})
        else:
            with open(file, "w", encoding="utf-8") as f:
                f.write("")
