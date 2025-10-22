import sqlite3
from datetime import datetime

conn = sqlite3.connect("users.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER,
    username TEXT,
    first_seen TEXT,
    last_active TEXT
)
""")
conn.commit()

def add_or_update_user(user_id, username):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cur.fetchone()

    if user:
        cur.execute("UPDATE users SET last_active=? WHERE user_id=?", (now, user_id))
    else:
        cur.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (user_id, username, now, now))
    conn.commit()

def get_user_count():
    cur.execute("SELECT COUNT(*) FROM users")
    return cur.fetchone()[0]
