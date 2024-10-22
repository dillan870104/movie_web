# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 16:29:29 2024

@author: dillan
"""
from selenium import webdriver as web
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def get_showtime_theater():
    place_dict = {}
    url = 'https://www.showtimes.com.tw/info/cinema'
    option = web.ChromeOptions()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    option.add_argument(f"user-agent={user_agent}")
    browser=web.Chrome(options=option)
    browser.implicitly_wait(5)
    browser.get(url)
    try:
        locator = (By.LINK_TEXT, '影城介紹')
        WebDriverWait(browser, 30, 0.5).until(EC.presence_of_element_located(locator))
        theater_elements = browser.find_elements(By.CLASS_NAME, "col-6.col-md-4")
        for theater_element in theater_elements:
            try:
                theater = theater_element.find_element(By.CLASS_NAME, "sc-fFlnrN.byra-dt")
                theater_name=theater.find_element(By.CLASS_NAME, "sc-kbdlSk.fgCmbm").text
                theater_place=theater.find_element(By.CLASS_NAME, "sc-camqpD.lmjUEm").text
                # print(theater_name)
                # print(theater_place)
                # print('/-----------------------/')
                place_dict[theater_name] = theater_place
            except Exception as e:
                print(f"錯誤:{e}")
            
    except Exception as e:
        print(f"初始抓取电影列表时发生错误: {e}")
    
    finally:
        browser.quit()
    return place_dict

place_dict = get_showtime_theater()
for k,i in place_dict.items():
    print(k,i)

