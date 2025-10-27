from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL
import subprocess, os
from config import DOWNLOAD_PATH
from utils import log_error, clean_filename

async def search_youtube(query, limit=10):
    try:
        search = VideosSearch(query, limit=limit)
        res = search.result()
        items = res.get("result", []) if isinstance(res, dict) else []
        good = []
        for v in items:
            title = v.get("title")
            link = v.get("link")
            duration = v.get("duration") or "—"
            thumbs = v.get("thumbnails") or []
            thumb = thumbs[0]["url"] if thumbs else None
            views = v.get("viewCount", {}).get("text", "—") if isinstance(v.get("viewCount"), dict) else v.get("viewCount", "—")
            published = v.get("publishedTime") or "—"
            if title and link:
                good.append({
                    "title": clean_filename(title),
                    "link": link,
                    "duration": duration,
                    "thumbnail": thumb,
                    "views": views,
                    "published": published
                })
        return good
    except Exception as e:
        log_error(f"search_youtube error: {e}")
        return []

async def download_mp3(url):
    ydl_opts = {"outtmpl": f"{DOWNLOAD_PATH}/%(title)s.%(ext)s", "format":"bestaudio/best", "quiet":True, "noplaylist":True}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        mp3_path = os.path.splitext(file_path)[0] + ".mp3"
        subprocess.run(["ffmpeg","-y","-i",file_path,"-vn","-ab","192k","-ar","44100",mp3_path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(file_path)
        return mp3_path
    except Exception as e:
        log_error(f"download_mp3 error: {e}")
        return None
