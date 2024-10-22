from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
from datetime import datetime

def initialize_driver():
    """初始化 WebDriver"""
    driver = webdriver.Chrome()
    driver.get("https://www.ambassador.com.tw/home/MovieList?Type=1")
    # 使用顯性等待，確保 JavaScript 完全加載
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.title"))
    )
    return driver

def get_movie_links(driver):
    """抓取電影清單頁面的所有電影連結"""
    soup = BeautifulSoup(driver.page_source, "html.parser")
    titles = soup.select("div.title a")
    movie_links = []
    
    for title in titles:#控制筆數
        movie_url = title.get("href")
        if not movie_url.startswith("http"):
            movie_url = "https://www.ambassador.com.tw/" + movie_url
        movie_links.append(movie_url)
    
    return movie_links

def parse_movie_page(movie_url):
    """解析單部電影的詳細頁面並提取所需的資訊"""
    r2 = requests.get(movie_url)
    if r2.status_code == 200:
        soup2 = BeautifulSoup(r2.text, "html.parser")

        # 取得中文與英文名稱，增加 None 檢查
        movie_name_zh_tag = soup2.select_one("li.disabled")
        movie_name_zh = movie_name_zh_tag.text.strip() if movie_name_zh_tag else "N/A"

        movie_name_en_tag = soup2.select_one("section#movie-info h6")
        movie_name_en = movie_name_en_tag.text.strip() if movie_name_en_tag else "N/A"
        
        #新增的
        assignment = soup2.find('div',class_='cell small-12 medium-12 large-12 movie-info-box').find('p').text.strip()
        if len(soup2.find('div',class_='rating-box').find_all('span')) !=2:
            level = 'N/A'
            movie_long = soup2.find('div',class_='rating-box').find_all('span')[0].text
        else:
            level = soup2.find('div',class_='rating-box').find_all('span')[0].text
            movie_long = soup2.find('div',class_='rating-box').find_all('span')[1].text
        img_src = soup2.find('div',class_='cell small-3 medium-2 large-2 movie-pic-box').find('img').get('src')
        
        # 提取導演、演員和影片類型，增加 None 檢查
        director_tag = soup2.select_one("li.director > p")
        director = director_tag.text.strip() if director_tag else "N/A"

        actors_tag = soup2.select_one("li.actors > p")
        actors = actors_tag.text.strip().replace('\n', ', ') if actors_tag else "N/A"

        genre_tag = soup2.select_one("li.genre > p")
        genre = genre_tag.text.strip() if genre_tag else "N/A"

        # 提取上映日期等其他資訊，增加 None 檢查
        release_date = "N/A"
        genre_from_note = "N/A"
        main_actors = "N/A"

        notes = soup2.select("p.note")
        for note in notes:
            if "上映日期" in note.text:
                release_date = note.text.replace("上映日期：", "").strip().replace('/','-')
            elif "影片類型" in note.text:
                genre_from_note = note.text.replace("影片類型：", "").strip()
            elif "主要演員" in note.text:
                main_actors = note.text.replace("主要演員：", "").strip()
            

        return {
            "Movie (Chinese)": movie_name_zh,
            "Movie (English)": movie_name_en,
            "Release Date": release_date,
            "Director": director,
            "Actors": main_actors,
            'Level':level,
            'Length':movie_long,
            "Genre": genre_from_note,
            'Assignment':assignment,
            'Img_src':img_src
        }

    return None

def get_movie_showtimes(soup2):
    """解析電影的場次資訊"""
    movie_showtimes = []
    theaters = soup2.select("div.theater-box>h3>a")
    theater_classes = soup2.select("div.theater-box>p")
    theater_times = soup2.select("div.theater-box h6")
    theater_seats = soup2.select("span.float-left.info")
    dates = soup2.select("#search-bar-page > div > div > div:nth-child(1) > ul > li > ul > li > a")
    #新增的
    theater_places = soup2.select("div.theater-box>h3>span.show-for-medium")
    
    for st, sc,tp in zip(theaters, theater_classes,theater_places[::3]):
        cinema_name = st.text.strip()
        for date, ti, ts in zip(dates, theater_times, theater_seats):#新增places
            time_info = ti.text.strip() if ti else "N/A"
            seat_info = ts.text.strip() if ts else "N/A"
            date_info = date.text.strip() if date else "N/A"
            date_info = date_info.split(',')[-1].strip()
            date_info = datetime.strptime(date_info, "%Y/%m/%d")

            
            place_info = tp.text.strip() if tp else 'N/A'
            movie_showtimes.append({
                "Cinema": cinema_name,
                'theater_classes':sc.text.split(')')[0]+')',
                "Date": date_info,
                "Time": time_info,
                "Seat Info": seat_info,
                'theater_places':place_info
            })

    return movie_showtimes

def scrape_movies():
    """主控制函式，抓取電影並返回電影資料的列表"""
    driver = initialize_driver()
    movie_links = get_movie_links(driver)
    all_movie_data = []

    for movie_url in movie_links:
        movie_data = parse_movie_page(movie_url)
        if movie_data:
            # 解析場次資訊並將其合併到電影資料中
            r2 = requests.get(movie_url)
            soup2 = BeautifulSoup(r2.text, "html.parser")
            showtimes = get_movie_showtimes(soup2)
            movie_data["Showtimes"] = showtimes
            all_movie_data.append(movie_data)
            print(f"已抓取: {movie_data['Movie (Chinese)']}")

    driver.quit()
    return all_movie_data

# 主程式呼叫
if __name__ == "__main__":
    movies = scrape_movies()

    # 顯示結果
    for movie in movies:
        print(movie)



