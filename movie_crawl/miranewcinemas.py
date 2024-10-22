from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from datetime import datetime
def fetch_showtimes():
    """主函數，爬取影城資訊並儲存電影時刻表至列表"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)
    year = datetime.today().year #今年
    now = datetime.today()
    now = now.date()
    try:
        driver.get('https://www.miranewcinemas.com/Booking/Timetable')

        # 等待下拉選單變得可選
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'sel_cinema')))
        
        # 定義所有影城名稱
        visible_texts = ['美麗新台茂影城 Tai-Mall Cinema', '美麗新淡海影城 Dan-Hai Cinema', '美麗新宏匯影城 Hon-Hui Cinema', '美麗新大直皇家影城 Da-Zhi Royal Cinema']
        places = ['桃園市蘆竹區南崁路一段112號7樓','新北市淡水區義山路二段303號 2F','新北市新莊區新北大道4段3號8樓','台北市中山區北安路780號B2']
        select_element = driver.find_element(By.ID, 'sel_cinema')
        select = Select(select_element)

        # 初始化所有電影時刻資訊的列表
        all_showtimes_data = []

        for visible_text in visible_texts[0:2]:#測試比數調整
            select.select_by_visible_text(visible_text)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'MovieCName')))
            
            r = driver.page_source
            soup = bs(r, 'html.parser')

            titles = soup.find_all(class_='MovieCName')
            titles_en = soup.find_all(class_='MovieEName')
            durations = soup.find_all(class_='MovieDuration')
            date_bars = driver.find_elements(By.CLASS_NAME, 'ShowDateList')
            img_rs = soup.select('div.movie_post.col.movie_post_pc>img')
            t_name = visible_text
            for i in range(len(visible_texts)):
                if visible_text==visible_texts[i]:
                    place = places[i]
            for n, (title, title_en, duration, date_bar, img_r) in enumerate(zip(titles, titles_en, durations, date_bars, img_rs)):
                dates = date_bar.find_elements(By.CLASS_NAME, 'movie_date')

                for i, date in enumerate(dates):
                    date.click()
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'movie_date')))
                    
                    r2 = driver.page_source
                    soup2 = bs(r2, 'html.parser')
                    show_date = soup2.find_all(class_='movie_date')[i].text.split('(')[0].strip()
                    
                    show_date_str = str(year)+'/' + show_date #str版
                    show_date_temp = datetime.strptime(show_date_str, "%Y/%m/%d") #時間版
                    if show_date_temp.date() < now:
                        year += 1
                        show_date_str = str(year) + '/' + show_date

                    show_date =  datetime.strptime(show_date_str, "%Y/%m/%d").date()  
                    # 提取電影場次資訊
                    movie_times = soup2.find_all(class_='movie_list row')
                    cinema_types = movie_times[n].find_all(class_='movie_time row')

                    for cinema_type in cinema_types:
                        cinema_name = cinema_type.find(class_='MovieHallCht col').text
                        for movie_time in cinema_type.find_all(class_='a_st'):
                            showtime = movie_time.text

                            # 儲存到結構化的字典
                            showtimes_data = {
                                '電影名稱': title.text,
                                '日期': show_date,
                                '時刻': showtime,
                                '影廳': cinema_name,
                                '影院名稱':t_name,
                                '地點':place,
                            }
                            all_showtimes_data.append(showtimes_data)

        return all_showtimes_data

    finally:
        driver.quit()  # 確保無論是否出現錯誤都能正確關閉 driver
        print("所有影城資訊爬取完畢。")

if __name__ == "__main__":
    # 執行主程式並取得資料
    showtimes_list = fetch_showtimes()
    print(showtimes_list)

