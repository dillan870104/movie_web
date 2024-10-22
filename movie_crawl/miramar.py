import requests
from bs4 import BeautifulSoup
from datetime import datetime


def miramar_update():
    url = "https://www.miramarcinemas.tw/timetable"
    r = requests.get(url)
    year = datetime.today().year #今年
    now = datetime.today()
    now = now.date()
    movie_level_list = ['badge_movie_level level_g','badge_movie_level level_p','badge_movie_level level_pg12','badge_movie_level level_pg15','badge_movie_level level_r']
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, "html.parser")
        movies = soup.find_all("div", class_="timetable_list row")
        miramarList = []
        for _movie in movies:  # 每一筆電影資料重複做一樣的事
            
            bookingDates = _movie.find("div", "block booking_date_area").find_all("a")
            date = []  # 所有場次日期
            roomlist = []  # 所有廳 room
            for bookingDate in bookingDates:
                date.append(bookingDate.get("id").split("_")[-1])

            tType = len(set(_movie.find_all("div", class_="room")))  # 放映廳種類數量
            rooms = _movie.find_all("div", class_="room")
            for room in rooms:
                roomlist.append(room.text.strip("watch_later"))
            timeAreas = _movie.find_all("div", class_="time_area")
            tal = []  # textAreaList
            for timeArea in timeAreas:
                tal.append(timeArea.text.split("\n")[1:-1])

            title = _movie.find("div", class_="title").text
            title_en = _movie.find("div", class_="title_en").text
            for level in movie_level_list: #判斷分級
                try:
                    movie_level = _movie.find('div',class_=level).text
                    break
                except:
                    movie_level = '未定'
            imgSrc = _movie.find("img").get("src")
            time = _movie.find("p", class_="time").text
            movieDetail = "https://www.miramarcinemas.tw" + _movie.find(
                "div", class_="col m4 s5"
            ).find("a").get("href")
            rs = requests.get(movieDetail)
            soup = BeautifulSoup(rs.text, "html.parser")
            movieInfoItem = soup.find("ul", class_="movie_info_item").find_all("li")

            releaseDate = movieInfoItem[0].text.split("上映 RELEASE DATE")[-1].strip()
            genre = movieInfoItem[1].text.split("類型 GENRE")[-1].strip()
            director = movieInfoItem[2].text.split("導演 DIRECTOR")[-1].strip()
            cast = movieInfoItem[3].text.split("演員CAST")[-1].strip()

            assignment = (
                soup.find("div", class_="col m6 s12")
                .text.split("劇情簡介:")[-1]
                .strip()
            )
            
            miramar = [title,title_en,time,imgSrc,releaseDate,genre,director,cast,assignment,movie_level]


            # 每天的時間場次(正常情況)
            if len(tal) % tType == 0:
                for i in range(0, len(tal), tType):
                    temp = []
                    temp += miramar  # 初始化場次以外的資料
                    today = date[int(i / tType)]
                    
                    today_str = str(year)+'年' + today #str版
                    today_temp = datetime.strptime(today_str, "%Y年%m月%d日") #時間版
                    if today_temp.date() < now:
                        year += 1
                        today_str = str(year) + '年' + today

                    today =  datetime.strptime(today_str, "%Y年%m月%d日").date()        
                    if tType == 1:
                        for j in tal[i]:
                            temp.append(today)
                            temp.append(roomlist[i])
                            temp.append(j)
                            miramarList.append(temp)
                            temp = []
                            temp += miramar

                    elif tType == 2:
                        for j in tal[i]:
                            temp.append(today)
                            temp.append(roomlist[i])
                            temp.append(j)
                            miramarList.append(temp)
                            temp = []
                            temp += miramar

                        for j in tal[i + 1]:
                            temp.append(today)
                            temp.append(roomlist[i + 1])
                            temp.append(j)
                            miramarList.append(temp)
                            temp = []
                            temp += miramar
                    elif tType == 3:
                        for j in tal[i]:
                            temp.append(today)
                            temp.append(roomlist[i])
                            temp.append(j)
                            miramarList.append(temp)
                            temp = []
                            temp += miramar

                        for j in tal[i + 1]:
                            temp.append(today)
                            temp.append(roomlist[i + 1])
                            temp.append(j)
                            miramarList.append(temp)
                            temp = []
                            temp += miramar
                        for j in tal[i + 2]:
                            temp.append(today)
                            temp.append(roomlist[i + 2])
                            temp.append(j)
                            miramarList.append(temp)
                            temp = []
                            temp += miramar

    return miramarList


if __name__ == "__main__":
    miramarlist=miramar_update()
    print(miramarlist)
