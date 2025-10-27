import json, re
from datetime import datetime
from config import LOG_FILE, USER_FILE, ERROR_LOG

def log_error(text: str):
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {text}\n")

def clean_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name) if name else "unknown"

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
