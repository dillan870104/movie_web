import requests as rq
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

# 設置請求頭
header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
}
sess = rq.Session()


# 擴充抓取位置
def get_place():
    place_data = []
    url = "https://www.vscinemas.com.tw/vsweb/theater/index.aspx"
    r = rq.get(url)
    if r.status_code == rq.codes.ok:
        soup = bs(r.text, "html.parser")
        theaters = soup.find_all("section", class_="infoArea")

        for theater in theaters:
            name = theater.find("h2").text
            place = theater.find("p", class_="icon-marker").text.strip("影城地址：")
            # print(name,place)
            place_data.append([name, place])
    place_data.append(["MUVIE CINEMAS", "台北市信義區松仁路58號10樓 (遠百信義A13)"])
    return place_data


# 定義函式
def fetch_movie_data(page_count=3):
    movie_data_list = []
    level_dict = {
        "teenager": "輔15級",
        "general": "普遍級",
        "adult": "限制級",
        "bigchild": "輔12級",
        "childview": "保護級",
    }
    place_data = get_place()
    # 使用上下文管理器啟動瀏覽器
    with webdriver.Chrome() as driver:
        for p in range(1, page_count + 1):  # 根據傳入的頁數來遍歷
            driver.get(f"https://www.vscinemas.com.tw/vsweb/film/index.aspx?p={p}")

            # 使用顯式等待確保頁面加載完成
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.movieList a>img"))
            )

            # 獲取頁面源代碼並解析
            r = driver.page_source
            soup = bs(r, "html.parser")

            # 獲取電影標題和鏈接
            movies = soup.select("ul.movieList a>img")
            links = soup.select("ul.movieList>li>figure>a")
            page_count = soup.find("section", class_="pagebar").find_all("a")[-2].text

            # print(max_page)
            # print(f'正在處理第 {p} 頁')

            for title, l in zip(movies, links):  # 測試改這
                # 濾掉沒有標題或不相關的條目
                if title.get("title") is None or "下載最新版" in title.get("title"):
                    continue

                print(f'電影標題: {title.get("title")}')

                # 嘗試使用 GET 請求來獲取電影詳細資訊
                movie_url = "https://www.vscinemas.com.tw/vsweb/film/" + l.get("href")
                try:
                    r = sess.get(movie_url, headers=header)
                    r.raise_for_status()  # 檢查請求是否成功
                    r = r.text
                except rq.RequestException as e:
                    print(f"訪問電影頁面失敗: {e}")
                    continue

                # 解析電影頁面
                soup = bs(r, "html.parser")

                # 抓取導演、演員、類型資訊
                try:
                    img_url = (
                        "https://www.vscinemas.com.tw/vsweb/"
                        + soup.find("div", class_="movieMain")
                        .find("img")
                        .get("src")[3:]
                    )
                    entitle = soup.find("div", class_="titleArea").find("h2").text
                    release_date = (
                        soup.find("div", class_="titleArea")
                        .find("time")
                        .text.strip("上映日期：")
                        .replace("/", "-")
                    )
                    info = soup.find("table").find_all("td")
                    director = info[1].text.strip() if info[1] != "" else "N/A"
                    actors = info[3].text.strip() if info[3] != "" else "N/A"
                    genre = info[5].text.strip() if info[5] != "" else "N/A"
                    movie_length = info[7].text.strip() if info[7] != "" else "N/A"
                    level = (
                        soup.find("div", class_="markArea").find("span").get("class")[0]
                    )
                    if level in level_dict:
                        level = level_dict[level]
                except:
                    if info == []:
                        director = "N/A"
                        actors = "N/A"
                        genre = "N/A"
                        movie_length = "N/A"
                        level = "N/A"

                # 抓取劇情簡介
                synopsis_section = soup.find("div", class_="bbsArticle")
                synopsis_paragraphs = synopsis_section.find_all("p")

                synopsis = []
                for p in synopsis_paragraphs:
                    if "全台預售情報" in p.get_text(strip=True):
                        break  # 遇到包含關鍵字的段落，停止抓取
                    synopsis.append(p.get_text(strip=True))

                synopsis = " ".join(synopsis) if synopsis else "N/A"
                # 抓取放映版本與時間等資訊
                Vlist = soup.select("li>a.versionFirst")
                MV = soup.select_one("div.movieVersion").text.split("\n")
                movieTime = soup.select("div.movieTime>article.hidden.article")

                inx = 0
                VV = [v.text for v in Vlist]
                (
                    dates,
                    mvv,
                    vvv,
                    tim,
                    moviestitle,
                    directors,
                    actors_list,
                    genres,
                    movie_length_list,
                    synopses,
                    img_urlList,
                    entitleList,
                    releasedateList,
                    placeList,
                    level_list,
                ) = ([], [], [], [], [], [], [], [], [], [], [], [], [], [], [])

                for vv in VV:
                    c = ""
                    for mv in MV:
                        if mv in VV:
                            if mv == vv:
                                c = "open"
                                continue
                            elif mv != vv:
                                c = "close"
                                continue
                        if (
                            mv != "*請選擇放映版本及影廳，場次將列於下方"
                            and mv != "放映版本"
                            and mv != ""
                            and c == "open"
                        ):
                            date = ""
                            # 這裡增加檢查
                            movie_time_text = movieTime[inx].text
                            split_result = movie_time_text.split(
                                "*所有售票通路同步開放購票(另有公告之場次除外)，黃色底時間代表即將售完/紅色底時間為完售，實際剩餘座位數請洽影城售票窗口"
                            )

                            # 檢查 split 是否有至少兩個元素
                            if len(split_result) > 1:
                                time_blocks = split_result[1].split(
                                    "\n\n"
                                )  # 取得時間部分
                            else:
                                # 如果無法正確分割，繼續下一個迭代，或者提供備用方案
                                print(f"無法解析時間資料: {movie_time_text}")
                                inx += 1
                                continue  # 跳過此迭代

                            for i in time_blocks:
                                if i != "" and len(i) == 5:  # 表示這是時間，例如 00:25
                                    tim.append(i)  # 保存時間
                                    mvv.append(mv)
                                    vvv.append(vv)
                                    moviestitle.append(
                                        title.get("title").replace("-", "")
                                    )

                                    dates.append(date)  # 空日期，因為這是時間
                                    directors.append(director)
                                    actors_list.append(actors)
                                    genres.append(genre)
                                    movie_length_list.append(movie_length)
                                    synopses.append(synopsis)
                                    img_urlList.append(img_url)
                                    entitleList.append(entitle)
                                    releasedateList.append(release_date)
                                    level_list.append(level)
                                    for place in place_data:
                                        if mv == place[0]:
                                            placeList.append(place[1])
                                elif len(i) > 5:  # 表示這是日期或特殊情況
                                    i = i.replace("\n", "")

                                    # 特殊處理 00:00(隔日)
                                    if "(隔日)" in i:
                                        # 將時間部分提取出來，並將其標記為隔日
                                        time_part = i.split("(隔日)")[0].strip()
                                        if time_part == "00:00":
                                            # 如果時間是 00:00 並標記為隔日，處理為特殊標記
                                            time_part = "00:00 (隔日)"

                                        # 保留特殊標記時間
                                        tim.append(time_part)
                                        continue

                                    # 移除其他 "(隔日)"，保留正常時間
                                    i = i.replace("(隔日)", "").strip()

                                    try:
                                        # 嘗試解析日期，忽略時間
                                        date = datetime.strptime(
                                            i.split("星期")[0].strip(),
                                            "%Y 年 %m 月 %d 日",
                                        ).date()
                                    except ValueError as e:
                                        print(f"無法解析日期: {i}, 錯誤: {e}")
                                        continue

                            inx += 1

                # 將提取出的數據添加到列表中
                movie_data_list.extend(
                    zip(
                        moviestitle,
                        entitleList,
                        dates,
                        tim,
                        mvv,
                        vvv,
                        directors,
                        actors_list,
                        genres,
                        synopses,
                        img_urlList,
                        releasedateList,
                        movie_length_list,
                        placeList,
                        level_list,
                    )
                )

    return movie_data_list


# 主程式呼叫
if __name__ == "__main__":
    # 使用函式獲取電影數據
    movies = fetch_movie_data()  # 爬取4個頁面

    for movie in movies:
        print(movie)
