import os, json, re
from datetime import datetime
from config import LOG_FILE, USER_FILE, ERROR_LOG

def log_error(msg: str):
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def clean_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name) if name else "unknown"

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Ensure log files exist
for file in [LOG_FILE, USER_FILE]:
    if not os.path.exists(file):
        save_json(file, {})
