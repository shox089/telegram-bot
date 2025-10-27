from youtubesearchpython import VideosSearch
from utils import clean_filename, log_error

async def search_youtube(query, limit=10):
    try:
        search = VideosSearch(query, limit=limit)
        items = search.result().get("result", [])
        results = []
        for v in items:
            title, link = v.get("title"), v.get("link")
            if not title or not link: continue
            duration = v.get("duration", "—")
            thumb = v.get("thumbnails")[0]["url"] if v.get("thumbnails") else None
            views = v.get("viewCount", {}).get("text") if isinstance(v.get("viewCount"), dict) else v.get("viewCount") or "—"
            published = v.get("publishedTime") or v.get("published") or v.get("uploadedOn") or "—"
            results.append({
                "title": clean_filename(title),
                "link": link,
                "duration": duration,
                "thumbnail": thumb,
                "views": views,
                "published": published
            })
        return results
    except Exception as e:
        log_error(f"search_youtube error: {e}")
        return []
