import aiosqlite, json
from datetime import datetime
from config import DB_FILE
from utils import log_error

async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, songs_found INTEGER DEFAULT 0,
            top_artist TEXT, last_song TEXT, last_active TEXT, genres_json TEXT DEFAULT '{}', dark_mode INTEGER DEFAULT 0)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, title TEXT, artist TEXT,
            UNIQUE(user_id, title, artist))""")
        await db.commit()

async def update_user_stats(user_id, username, artist, title, genre=None):
    try:
        async with aiosqlite.connect(DB_FILE) as db:
            cur = await db.execute("SELECT songs_found, top_artist, genres_json FROM users WHERE user_id=?", (user_id,))
            row = await cur.fetchone()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if row:
                songs_found, top_artist, genres_json = row
                songs_found += 1
                genres = json.loads(genres_json or "{}")
                if genre: genres[genre] = genres.get(genre, 0) + 1
                await db.execute("UPDATE users SET songs_found=?, top_artist=?, last_song=?, last_active=?, genres_json=? WHERE user_id=?",
                    (songs_found, artist or top_artist, title, now, json.dumps(genres, ensure_ascii=False), user_id))
            else:
                genres = {genre:1} if genre else {}
                await db.execute("INSERT INTO users (user_id, username, songs_found, top_artist, last_song, last_active, genres_json) VALUES (?,?,?,?,?,?,?)",
                    (user_id, username, 1, artist, title, now, json.dumps(genres, ensure_ascii=False)))
            await db.commit()
    except Exception as e:
        log_error(f"update_user_stats error: {e}")
