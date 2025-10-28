from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from utils import load_json, log_error
from db import DB_FILE
import aiosqlite

scheduler = AsyncIOScheduler()

def scheduler_start(bot):
    """
    Scheduler ishga tushiradi va kunlik xulosani yuboradi.
    """
    scheduler.add_job(
        daily_summary,
        'interval',
        hours=24,
        next_run_time=datetime.now() + timedelta(seconds=10),
        kwargs={'bot': bot}
    )
    scheduler.start()


async def daily_summary(bot):
    """
    Har bir foydalanuvchiga kunlik xulosa xabarini yuboradi.
    """
    try:
        users = load_json("users.json")
        if not users:
            return

        async with aiosqlite.connect(DB_FILE) as db:
            for uid_str in users.keys():
                try:
                    uid = int(uid_str)
                    cur = await db.execute("SELECT songs_found FROM users WHERE user_id=?", (uid,))
                    row = await cur.fetchone()
                    count = row[0] if row else 0
                    await bot.send_message(uid, f"📅 Kunlik xulosa:\n🎧 Siz hozirgacha {count} ta qo‘shiq topdingiz.")
                except Exception as e:
                    log_error(f"daily_summary error for {uid_str}: {e}")

    except Exception as e:
        log_error(f"daily_summary global error: {e}")
