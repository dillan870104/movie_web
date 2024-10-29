from apscheduler.schedulers.blocking import BlockingScheduler
from concurrent.futures import ThreadPoolExecutor
from showtime import showtime_update  # 載入你的 showtime_update 函數
from ambassador import scrape_movies
# from vieshow import fetch_movie_data
from miranewcinemas import fetch_showtimes
from miramar import miramar_update

# 建立排程器
scheduler = BlockingScheduler()

# 建立執行緒池，允許多個任務同時執行
executor = ThreadPoolExecutor()

# 定義多工任務
def execute_all_tasks():
    # 提交所有任務給執行緒池，同時執行
    executor.submit(showtime_update)
    executor.submit(scrape_movies)
    # executor.submit(fetch_movie_data)
    executor.submit(fetch_showtimes)
    executor.submit(miramar_update)

# 每天中午12點執行所有任務
scheduler.add_job(execute_all_tasks, 'cron', hour=15, minute=55)

# 每4個小時執行一次所有任務
# scheduler.add_job(execute_all_tasks, 'interval', minutes=2)

# 開始排程
try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    pass
