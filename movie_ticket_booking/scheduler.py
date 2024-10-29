from apscheduler.schedulers.background import BackgroundScheduler
from movie_crawl.showtime import showtime_update  # 從 showtime.py 匯入爬蟲函式
from movie_crawl.ambassador import scrape_movies
from movie_crawl.miramar import miramar_update
from movie_crawl.miranewcinemas import fetch_showtimes
from movie_crawl.vieshow import fetch_movie_data
from apscheduler.executors.pool import ThreadPoolExecutor
import time
from movie_ticket_booking.views import movie_update


# 設定 ThreadPoolExecutor，允許最多 5 個任務同時執行
executors = {"default": ThreadPoolExecutor(5)}


def setup_scheduler():
    scheduler = BackgroundScheduler()

    # # 每天 24:00 執行一次
    # scheduler.add_job(showtime_update, "cron", hour=0, minute=0)

    # # 每天 24:00 執行一次
    # scheduler.add_job(scrape_movies, "cron", hour=0, minute=0)

    # # 每天 24:00 執行一次
    # scheduler.add_job(miramar_update, "cron", hour=0, minute=0)

    # # 每天 24:00 執行一次
    # scheduler.add_job(fetch_showtimes, "cron", hour=0, minute=0)

    # # 每天 24:00 執行一次
    # scheduler.add_job(fetch_movie_data, "cron", hour=0, minute=0)
    # 每 30 分鐘執行一次
    scheduler.add_job(miramar_update, "interval", minutes=2)

    scheduler.start()
    print("排程已啟動...")

    try:
        # 主程式保持運行
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("正在關閉排程器...")
        scheduler.shutdown()
        print("排程器已停止")


if __name__ == "__main__":
    setup_scheduler()
