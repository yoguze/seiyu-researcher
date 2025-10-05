# scraper.py
"""
Google News RSS を利用した声優ニュース取得スクレイパー
- KEYWORDS: リストで複数キーワードを指定
- RSSからURL・タイトル・公開日を取得
- 重複排除して最新MAX_ITEMS件まで
- update_news() がキャッシュ更新
"""

import feedparser
from datetime import datetime, timezone, timedelta
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- 設定 ----------
KEYWORDS = ["石見舞菜香","岡崎美保","長谷川育美","東山奈央","青山吉能","鬼頭明里","高橋李依","赤尾ひかる"]
RSS_URL = "https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
MAX_ITEMS = 20
# --------------------------

_cached_news = []
_last_updated = None

def fetch_news(max_items=MAX_ITEMS):
    results = []
    seen_links = set()

    for kw in KEYWORDS:
        url = RSS_URL.format(query=kw.replace(" ", "+"))
        logger.info(f"Fetching RSS for keyword: {kw} -> {url}")

        feed = feedparser.parse(url)

        for entry in feed.entries:
            link = entry.link
            title = entry.title

            # 重複排除
            if link in seen_links:
                continue
            seen_links.add(link)

            # 日付取得（published_parsed があれば使う）
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            else:
                published_at = None

            results.append({
                "title": title,
                "link": link,
                "published_at": published_at.isoformat() if published_at else None
            })

        time.sleep(0.2)  # RSS連続アクセスの負荷軽減

    # 公開日時でソート（Noneは後ろ）
    results_sorted = sorted(
        results,
        key=lambda x: datetime.fromisoformat(x["published_at"]) if x["published_at"] else datetime.min,
        reverse=True
    )

    return results_sorted[:max_items]

def update_news():
    global _cached_news, _last_updated
    logger.info("Updating cached news...")
    try:
        _cached_news = fetch_news(MAX_ITEMS)
        _last_updated = datetime.now(timezone.utc)
        logger.info(f"Cache updated: {len(_cached_news)} items (at {_last_updated.isoformat()})")
    except Exception as e:
        logger.exception(f"Failed to update news: {e}")

def get_news():
    return list(_cached_news)

def get_last_updated():
    return _last_updated
