from selenium import webdriver as web
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import json


# ===============================================
# 关闭模态弹窗
def get_pic():
    url = "https://capi.showtimes.com.tw/1/app/bootstrap"
    request = requests.get(url)
    movielist = request.json()
    movie_dict = {}
    for movie in movielist["payload"]["programs"]:
        # print(movie['name'],movie['coverImagePortrait']['url'])
        movie_dict[movie["name"]] = movie["coverImagePortrait"]["url"]
    return movie_dict


def showtime_update():
    # 爬取所有地點資訊
    def get_showtime_theater():
        place_dict = {}
        url = "https://www.showtimes.com.tw/info/cinema"
        option = web.ChromeOptions()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        option.add_argument(f"user-agent={user_agent}")
        browser = web.Chrome(options=option)
        browser.implicitly_wait(5)
        browser.get(url)
        try:
            locator = (By.LINK_TEXT, "影城介紹")
            WebDriverWait(browser, 30, 0.5).until(
                EC.presence_of_element_located(locator)
            )
            theater_elements = browser.find_elements(By.CLASS_NAME, "col-6.col-md-4")
            for theater_element in theater_elements:
                try:
                    theater = theater_element.find_element(
                        By.CLASS_NAME, "sc-fFlnrN.byra-dt"
                    )
                    theater_name = theater.find_element(
                        By.CLASS_NAME, "sc-kbdlSk.fgCmbm"
                    ).text
                    theater_place = theater.find_element(
                        By.CLASS_NAME, "sc-camqpD.lmjUEm"
                    ).text
                    print(theater_name)
                    print(theater_place)
                    print("/-----------------------/")
                    place_dict[theater_name] = theater_place
                except Exception as e:
                    print(f"錯誤:{e}")

        except Exception as e:
            print(f"初始抓取电影列表时发生错误: {e}")

        finally:
            browser.quit()
        return place_dict

    def close_modal_if_present(driver):
        try:
            close_button = driver.find_element(By.CSS_SELECTOR, ".modal .close-button")
            close_button.click()
            print("模态弹窗已关闭")
        except NoSuchElementException:
            print("无模态弹窗")

    # 处理弹窗函数
    def handle_popups(driver):
        close_modal_if_present(driver)
        main_window = driver.current_window_handle
        all_windows = driver.window_handles
        if len(all_windows) > 1:
            for window in all_windows:
                if window != main_window:
                    driver.switch_to.window(window)
                    driver.close()
                    print("新窗口已关闭")
            driver.switch_to.window(main_window)

    # ===============================================
    # 获取时间表信息
    def _time():
        theater_times_dict = {}  # 用於存儲影院與時間的字典

        try:
            # 查找日期部分中的所有日期項目
            date_elements = WebDriverWait(myW, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "sc-iMTnTL"))
            )
        except Exception as e:
            print(f"無法找到日期部分: {e}")
            return {}

        first_date_element = None  # 存储第一个日期元素

        # 遍歷每個日期元素
        for index, date_element in enumerate(date_elements):
            try:
                # 保存第一个日期元素
                if index == 0:
                    first_date_element = date_element

                # 提取日期和星期文本
                date_info = " ".join(
                    [
                        span.text.strip()
                        for span in date_element.find_elements(By.TAG_NAME, "span")
                    ]
                )

                # 點擊日期元素，顯示對應的影院時間
                WebDriverWait(myW, 10).until(
                    EC.element_to_be_clickable(date_element)
                ).click()

                # 提取影院信息
                theater_elements = WebDriverWait(myW, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CLASS_NAME, "sc-kAkpmW.jGVzdH")
                    )
                )

                time_data = {}  # 存儲每個影院的時間信息

                for theater_element in theater_elements:
                    theater_name = theater_element.find_element(
                        By.CLASS_NAME, "sc-gFVvzn.eECWsO"
                    ).text.strip()
                    theater_playtype = theater_element.find_element(
                        By.CLASS_NAME, "sc-brPLxw.fHYMVe.d-none.d-md-block"
                    ).text.strip()

                    # 提取該影院所有的時間選項
                    time_buttons = theater_element.find_elements(
                        By.CLASS_NAME,
                        "sc-iGgWBj.ffxCYX.btn.sc-bBeLUv.enqmAq.mr-2.mb-2.py-2.btn-outline-primary",
                    )
                    time_list = [btn.text.strip() for btn in time_buttons]

                    time_data[theater_name, theater_playtype] = (
                        time_list  # 將影院名與時間列表存入字典+放映類型
                    )

                # 存儲該日期對應的影院與時間信息
                theater_times_dict[date_info] = time_data

            except Exception as e:
                print(f"處理日期 {date_info} 時發生錯誤: {e}")

        # 返回到第一个日期按钮
        if first_date_element:
            first_date_element.click()
            print("已返回到第一个日期按钮")

        # 返回影院與時間信息字典
        return theater_times_dict

    # ===============================================
    # 抓取电影信息的函数
    # ===============================================
    # 抓取电影信息的函数
    def _movie():
        # 定义字典存储电影信息
        level_dict = {
            "sc-Nxspf bBNyxX": "輔15級",
            "jJjFeP": "普遍級",
            "hFtxOS": "限制級",
            "fbrkXM": "輔12級",
            "fYlZNI": "保護級",
        }
        moviE = {}
        texT = myW.page_source
        mySoup = BeautifulSoup(texT, "lxml")

        # 获取中文片名
        moviE["中文片名"] = mySoup.select_one("div.sc-jnOGJG.mQyVn").text.strip()
        # 获取英文片名
        moviE["英文片名"] = mySoup.select_one("div.sc-dZoequ.gdfOVW").text.strip()

        # 获取其他电影信息
        find_rule = mySoup.select(
            "div.sc-cmaqmh.bIIkFl"
        )  # 包含级别、时长、上映日、类型、演员、导演、简介
        if find_rule:

            level = (
                find_rule[0].find("div").get("class")[-1]
                if len(find_rule) > 0
                else "N/A"
            )

            if level in level_dict:
                moviE["級別"] = level_dict[level]
            moviE["片長"] = find_rule[1].text.strip() if len(find_rule) > 1 else "N/A"
            moviE["上映日"] = find_rule[2].text.strip() if len(find_rule) > 2 else "N/A"
            moviE["類型"] = find_rule[4].text.strip() if len(find_rule) > 4 else "N/A"
            moviE["演員"] = find_rule[5].text.strip() if len(find_rule) > 5 else "N/A"
            moviE["導演"] = find_rule[6].text.strip() if len(find_rule) > 6 else "N/A"

            # 获取简洁内容，忽略 button 类别
            intro_elements = [
                elem
                for elem in find_rule[7].find_all(string=True)
                if elem.parent.name != "button"
            ]
            moviE["簡介"] = (
                "".join([elem.strip() for elem in intro_elements]).strip()
                if len(find_rule) > 7
                else "N/A"
            )

        # 获取电影时间表
        return moviE

    # ===============================================
    # 将time按钮信息逐个处理，并调用_movie
    def handle_time_buttons():
        # 获取所有`btn-outline-primary`按钮
        time_buttons = myW.find_elements(
            By.CLASS_NAME,
            "sc-iGgWBj.ffxCYX.btn.sc-jMakVo.jDptCM.mr-2.mb-2.py-2.px-4.btn-outline-primary",
        )

        # 遍历时间按钮
        for time_button in time_buttons:  # 測試按鈕數量([1:2])
            try:
                WebDriverWait(myW, 10).until(EC.element_to_be_clickable(time_button))
                time_button.click()  # 点击时间按钮以获取对应的时间信息

                # 调用_time获取时间表
                timE = _time()  # 获取时间表
                moviE = _movie()  # 获取其他电影信息
                moviE["時間"] = timE  # 添加时间信息到电影信息字典中

                movie_list.append(moviE)

            except Exception as e:
                print(f"点击时间按钮时发生错误: {e}")

    # ===============================================
    # 主流程
    pic_dict = get_pic()
    theater_dict = get_showtime_theater()
    oP = web.ChromeOptions()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    oP.add_argument(f"user-agent={user_agent}")
    myW = web.Chrome(options=oP)
    myW.implicitly_wait(2)
    myW.get("https://www.showtimes.com.tw/programs")

    movie_list = []
    try:
        locator = (By.LINK_TEXT, "快速訂票")
        WebDriverWait(myW, 30, 0.5).until(EC.presence_of_element_located(locator))
        # /---------------------測試數量------------------------------------/
        movie_elements = myW.find_elements(By.CLASS_NAME, "sc-dcJsrY.OvScF")
        # 測試數量用
        for index in range(len(movie_elements)):
            try:
                WebDriverWait(myW, 30).until(
                    EC.element_to_be_clickable(movie_elements[index])
                )
                movie_elements[index].click()

                handle_popups(myW)

                # 处理时间按钮
                handle_time_buttons()  # 逐个点击时间按钮，获取对应信息

            except Exception as e:
                print(f"点击或抓取电影时发生错误: {e}")

            finally:
                myW.back()  # 返回电影列表页面
                WebDriverWait(myW, 30, 0.5).until(
                    EC.presence_of_all_elements_located(
                        (By.CLASS_NAME, "sc-dcJsrY.OvScF")
                    )
                )
                movie_elements = myW.find_elements(By.CLASS_NAME, "sc-dcJsrY.OvScF")

    except Exception as e:
        print(f"初始抓取电影列表时发生错误: {e}")

    finally:
        myW.quit()

    # ===============================================
    year = datetime.today().year  # 今年
    now = datetime.today()
    now = now.date()
    dataList = []
    for movie in movie_list:
        chinese_name = movie["中文片名"]
        english_name = movie["英文片名"]
        level = movie.get("級別", "N/A")
        duration = movie.get("片長", "N/A")
        release_date = movie.get("上映日", "N/A").replace("/", "-")
        genre = movie.get("類型", "N/A")
        actors = movie.get("演員", "N/A")
        director = movie.get("導演", "N/A")
        introduction = movie.get("簡介", "N/A")
        times = movie["時間"]
        try:
            movie_pic = pic_dict[movie["中文片名"]]
        except:
            movie_pic = "N/A"

        # 输出每个個時間段都包含完整電影信息
        for date, theaters in times.items():
            date = date.split("日")[0].strip(" ")
            date_str = str(year) + "年" + date  # str版
            date_temp = datetime.strptime(date_str, "%Y年%m月%d")  # 時間版
            if date_temp.date() < now:
                year += 1
                date_str = str(year) + "年" + date

            date = datetime.strptime(date_str, "%Y年%m月%d").date()
            for theater, showtimes in theaters.items():
                for time in showtimes:
                    for i, j in theater_dict.items():
                        print(i, j)
                        print(theater[0])
                        if i.strip("影城") in theater[0]:
                            place = j
                            break
                        else:
                            place = "N/A"
                    data = {
                        "中文片名": chinese_name,
                        "英文片名": english_name,
                        "級別": level,
                        "片長": duration,
                        "上映日": release_date,
                        "類型": genre,
                        "演員": actors,
                        "導演": director,
                        "簡介": introduction,
                        "影廳": theater[0],
                        "日期": date,
                        "時間": time,
                        "播放種類": theater[1],
                        "影院位置": place,
                        "圖片網址": movie_pic,
                    }

                    dataList.append(data)
    return dataList
    print("電影资料已成功保存")


if __name__ == "__main__":
    sh = showtime_update()
