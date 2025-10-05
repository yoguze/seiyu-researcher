# app.py
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import scraper
import atexit
from datetime import datetime
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 初回キャッシュ更新（起動時）
scraper.update_news()

# スケジューラセットアップ（10分ごと）
scheduler = BackgroundScheduler()
scheduler.add_job(func=scraper.update_news, trigger="interval", minutes=10, id="update_news_job", replace_existing=True)
scheduler.start()

# Flask ルート
@app.route("/")
def index():
    news = scraper.get_news()
    last_updated = scraper.get_last_updated()
    if last_updated:
        # ローカル展示用に JST に変換して表示する（UTC stored）
        try:
            jst = last_updated.astimezone()
            last_str = last_updated.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            last_str = last_updated.strftime("%Y-%m-%d %H:%M:%S UTC")
    else:
        last_str = "更新されていません"
    return render_template("index.html", news=news, last_updated=last_str, keywords=scraper.KEYWORDS)

# アプリ終了時にスケジューラを停止
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
