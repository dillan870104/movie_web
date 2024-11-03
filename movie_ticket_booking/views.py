from django.shortcuts import render, redirect
from django.http import HttpResponse
from movie_ticket_booking.models import User, Movie, Show, TextBoard, Favorite, Theater
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from movie_ticket_booking.form import RegisterForm

# from sklearn import svm
# from sklearn.preprocessing import MultiLabelBinarizer
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score


import random

# 排程測試
# from .task import (
#     run_showtimes_task,
#     run_vieshow_task,
#     run_ambassador_task,
#     run_miramar_task,
#     run_miranewcinemas_task,
# )


# 寄送驗證信
def send_verify(email, verify):

    email = email
    subject = "驗證您的電子郵件地址"
    text_content = f"這是一封驗證信，請輸入下方驗證碼以下完成驗證\n\n"
    sender_email = "shiguangmulian@gmail.com"
    recipient_email = f"{email}"
    html_content = f"""
        <h1>歡迎加入我們的會員！</h1>
        <p>親愛的會員您好：</p>
        <p>這是一封會員驗證信。</p>
        
        <p>您的註冊驗證碼為:{verify}</p>
        
        
        </blockquote>
        """
    msg = EmailMultiAlternatives(subject, text_content, sender_email, [recipient_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return [email, verify]


# Create your views here.
# 管理者管理資料
def db_control(request):
    user = request.session["username"]
    admin = request.session["admin"]

    if admin:
        return render(request, "admin.html", locals())
    else:
        user = None
        admin = None
        return render(request, "login.html", locals())


# 爬蟲
def movie_update(request, cinemaName):  # 所有電影清單更新在這
    user = request.session["username"]
    admin = request.session["admin"]
    mess = ""
    from movie_crawl import miramar, ambassador, miranewcinemas, vieshow, showtime

    # 爬蟲

    if cinemaName == "miramar":  # 美麗華
        # 跑miramar爬蟲
        miramarList = miramar.miramar_update()  # 跑miramar爬蟲取得資料
        # 存進資料庫的部分
        for miramar_movie in miramarList:
            # 判斷電影資訊是否存在
            if len(Movie.objects.filter(title=miramar_movie[0])) == 0:
                # 存進movie資料表
                Movie.objects.create(
                    title=miramar_movie[0],
                    title_en=miramar_movie[1],
                    time=miramar_movie[2].strip("片長:"),
                    img_src=miramar_movie[3],
                    release_date=miramar_movie[4],  # 2024-10-25
                    type=miramar_movie[5],
                    director=miramar_movie[6],
                    cast=miramar_movie[7],
                    assignment=miramar_movie[8],
                    level=miramar_movie[9],
                )
            else:  # 新增一個判斷電影類型標籤的判斷，若沒有這個類型標籤就加上去
                temp = Movie.objects.get(title=miramar_movie[0])
                if miramar_movie[5] not in temp.type:
                    temp.type = temp.type + "、" + miramar_movie[5]
                    temp.save()
            # 存進show資料表
            Movie.objects.get(title=miramar_movie[0]).theater_movie.create(
                theater_name="大直美麗華",
                place="台北市中山區敬業三路22號6樓",
                roomType=miramar_movie[11],
                date=miramar_movie[10],
                playTime=miramar_movie[12],
            )

    if cinemaName == "ambassador":  # 國賓
        ambassadorList = ambassador.scrape_movies()
        # 存進資料庫的部分
        for ambassador_movie in ambassadorList:
            if (
                len(Movie.objects.filter(title=ambassador_movie["Movie (Chinese)"]))
                == 0
            ):
                Movie.objects.create(
                    title=ambassador_movie["Movie (Chinese)"],
                    title_en=ambassador_movie["Movie (English)"],
                    time=ambassador_movie["Length"],
                    img_src=ambassador_movie["Img_src"],
                    release_date=ambassador_movie["Release Date"],
                    type=ambassador_movie["Genre"],
                    director=ambassador_movie["Director"],
                    cast=ambassador_movie["Actors"],
                    assignment=ambassador_movie["Assignment"],
                )
            else:  # 新增一個判斷電影類型標籤的判斷，若沒有這個類型標籤就加上去
                temp = Movie.objects.get(title=ambassador_movie["Movie (Chinese)"])
                if ambassador_movie["Genre"] not in temp.type:
                    temp.type = temp.type + "、" + ambassador_movie["Genre"]
                    temp.save()
            # 存進show資料表
            if ambassador_movie["Assignment"] != []:
                for showtime in ambassador_movie["Showtimes"]:
                    Movie.objects.get(
                        title=ambassador_movie["Movie (Chinese)"]
                    ).theater_movie.create(
                        theater_name=showtime["Cinema"],
                        place=showtime["theater_places"],
                        roomType=showtime["theater_classes"],
                        date=showtime["Date"],
                        playTime=showtime["Time"],
                    )

    if cinemaName == "vieshow":  # 威秀
        # 跑爬蟲
        vieshowList = vieshow.fetch_movie_data()
        # 存進資料庫的部分
        for vieshow_movie in vieshowList:
            if len(Movie.objects.filter(title=vieshow_movie[0])) == 0:
                Movie.objects.create(
                    title=vieshow_movie[0],
                    title_en=vieshow_movie[1],
                    time=vieshow_movie[12],
                    img_src=vieshow_movie[10],
                    release_date=vieshow_movie[11],
                    type=vieshow_movie[8].replace("/", "、"),
                    director=vieshow_movie[6],
                    cast=vieshow_movie[7],
                    assignment=vieshow_movie[9],
                    level=vieshow_movie[14],
                )
            else:  # 新增一個判斷電影類型標籤的判斷，若沒有這個類型標籤就加上去
                temp = Movie.objects.get(title=vieshow_movie[0])

                for t in vieshow_movie[8].replace("/", "、").split("、"):
                    if t not in temp.type:
                        temp.type = temp.type + "、" + t
                        temp.save()

            # 存進show資料表
            Movie.objects.get(title=vieshow_movie[0]).theater_movie.create(
                date=vieshow_movie[2],
                roomType=vieshow_movie[5],
                playTime=vieshow_movie[3],
                theater_name=vieshow_movie[4],
                place=vieshow_movie[13],
            )
    if cinemaName == "miranew":  # 美麗新
        # 跑爬蟲
        miranewList = miranewcinemas.fetch_showtimes()
        # 存進資料庫的部分
        for miranew_movie in miranewList:
            if len(Movie.objects.filter(title=miranew_movie["電影名稱"])) != 0:
                # 存進show資料表
                Movie.objects.get(title=miranew_movie["電影名稱"]).theater_movie.create(
                    date=miranew_movie["日期"],
                    roomType=miranew_movie["影廳"],
                    playTime=miranew_movie["時刻"],
                    theater_name=miranew_movie["影院名稱"],
                    place=miranew_movie["地點"],
                )
    if cinemaName == "showtime":
        showtimeList = showtime.showtime_update()
        # 存進資料庫的部分
        for showtime_movie in showtimeList:
            if len(Movie.objects.filter(title=showtime_movie["中文片名"])) == 0:
                Movie.objects.create(
                    title=showtime_movie["中文片名"],
                    title_en=showtime_movie["英文片名"],
                    time=showtime_movie["片長"],
                    img_src=showtime_movie["圖片網址"],
                    release_date=showtime_movie["上映日"],
                    type=showtime_movie["類型"].replace("，", "、"),
                    director=showtime_movie["導演"],
                    cast=showtime_movie["演員"],
                    assignment=showtime_movie["簡介"],
                    level=showtime_movie["級別"],
                )
            else:  # 新增一個判斷電影類型標籤的判斷，若沒有這個類型標籤就加上去
                temp = Movie.objects.get(title=showtime_movie["中文片名"])
                for t in showtime_movie["類型"].replace("，", "、").split("、"):
                    if t not in temp.type:
                        temp.type = temp.type + "、" + t
                        temp.save()
            # 存進show資料表
            print(showtime_movie["日期"])
            Movie.objects.get(
                title=showtime_movie["中文片名"],
            ).theater_movie.create(
                date=showtime_movie["日期"],
                roomType=showtime_movie["播放種類"],
                playTime=showtime_movie["時間"],
                theater_name=showtime_movie["影廳"],
                place=showtime_movie["影院位置"],
            )
        mess = f"{cinemaName}資料更新完成"

    return redirect("/db_control/")
    # return HttpResponse("電影資料更新完成")


def del_show(request, theaterName):
    # unit = Show.objects.all()
    if theaterName == "all":
        unit = Show.objects.all()
        unit.delete()
    else:
        unit = Show.objects.filter(theater_name__contains=theaterName)
        unit.delete()

    mess = f"{theaterName} 刪除完成"
    return redirect("/db_control/")


def movielist(request):
    try:
        movielist = Movie.objects.all()
        user = request.session["username"]
        admin = request.session["admin"]
        return render(request, "home.html", locals())
    except:
        movielist = Movie.objects.all()
        user = None
        admin = None
        return render(request, "home.html", locals())


def register(request):
    user = None
    admin = None
    if request.method == "POST":
        postform = RegisterForm(request.POST)
        print("測試開始")
        is_exist_acc = False
        is_exist_email = False
        # 判斷email與acc是否唯一
        if User.objects.filter(acc=postform.data.get("acc")).count():
            is_exist_acc = True
        else:
            is_exist_acc = False
        if User.objects.filter(email=postform.data.get("email")).count():
            is_exist_email = True
        else:
            is_exist_email = False
        if postform.is_valid() and not is_exist_acc and not is_exist_email:
            username = postform.cleaned_data["username"]
            acc = postform.cleaned_data["acc"]
            pwd = postform.cleaned_data["pwd"]
            email = postform.cleaned_data["email"]
            tel = postform.cleaned_data["tel"]

            registerdate = timezone.now()
            registerdate = registerdate.strftime("%Y-%m-%d %H:%M:%S")

            request.session["temp_username"] = username
            request.session["temp_acc"] = acc
            request.session["temp_pwd"] = pwd
            request.session["temp_email"] = email
            request.session["temp_tel"] = tel
            request.session["temp_registerdate"] = registerdate

            return redirect("/verify/")
        else:
            if is_exist_acc:
                postform.errors["acc"] = "帳號已存在"
            if is_exist_email:
                postform.errors["email"] = "信箱地址已存在"
            return render(request, "register.html", locals())

    else:
        user = None
        admin = None
        postform = RegisterForm()
    return render(request, "register.html", locals())


def verify(request):
    user = None
    admin = None
    if "temp_email" in request.session:  # 有資料就會寄驗證信
        print("有session")  # 測試
        email = request.session["temp_email"]
        try:
            email_msg = request.session["error_message"]
        except:
            email_msg = None
        verify = ""  # 6位數驗證碼
        for i in range(6):
            digi = random.randint(0, 9)
            verify += str(digi)
        request.session["verify"] = verify
        now = timezone.now()
        send_verify(email, verify)

        print(email, verify, now)
        test = now.timetz()
        print(test)

        return render(request, "verify.html", locals())
    else:
        print("沒有session")
        return redirect("/register/")


def check_ver(request):
    user = None
    admin = None
    if request.method == "POST":
        verify_code = request.POST.get("v_code")
        if verify_code == request.session["verify"]:
            mess = "註冊成功"
            unit = User.objects.create(
                username=request.session["temp_username"],
                acc=request.session["temp_acc"],
                pwd=request.session["temp_pwd"],
                email=request.session["temp_email"],
                tel=request.session["temp_tel"],
                registerdate=request.session["temp_registerdate"],
            )

            unit.save()
            request.session.clear()
            return render(request, "login.html", locals())
        elif verify_code != request.session["verify"]:

            return redirect("/verify/")


def login(request):
    user = None
    admin = None
    if request.method == "POST":
        acc = request.POST["acc"]
        pwd = request.POST["pwd"]

        try:
            db_data = User.objects.get(
                acc=acc
            )  # 根據表單輸入的acc找出資料庫對應帳號的資料
            if db_data.pwd == pwd:
                mess = "登入成功"
                request.session["acc"] = db_data.acc
                request.session["pwd"] = db_data.pwd
                request.session["username"] = db_data.username
                request.session["admin"] = db_data.admin_id

                return redirect("/index/")
            elif db_data.pwd != pwd:
                mess = "密碼錯誤"
                user = None
                admin = None
                return render(request, "login.html", locals())
            else:
                mess = "錯誤，請重新輸入"
                user = None
                admin = None
                return render(request, "login.html", locals())
        except:
            mess = "沒有此帳號，請重新輸入"
            user = None
            admin = None
            return render(request, "login.html", locals())

    else:
        user = None
        admin = None
        mess = "請輸入您的帳號與密碼"
        return render(request, "login.html", locals())


def logout(request):

    request.session.clear()

    return redirect("/index/")


def show_movie_info(request, movieId):
    try:
        if "username" in request.session:
            user = request.session["username"]
            admin = request.session["admin"]
        else:
            user = None
            admin = None
        movieId = movieId
        movie_info = Movie.objects.get(id=movieId)

        show_list = Show.objects.filter(movie_id=movieId)
        text_info = TextBoard.objects.filter(tb_movie_id=movieId)
        mess = "你的評論"
        return render(request, "movie_info.html", locals())
    except Exception as e:
        # print(e)
        return redirect("/index/")


def leave_comment(request, movieId):  # 留言板功能
    movie_info = Movie.objects.get(id=movieId)
    if "username" in request.session:
        user = request.session["username"]
        admin = request.session["admin"]
        if request.method == "POST":

            movieId = request.POST["id"]
            user = request.session["username"]
            comment_content = request.POST["comment"]
            comment_time = timezone.now()
            unit = Movie.objects.get(id=movieId).text_movie.create(
                tb_movie=movieId,
                tb_user=user,
                content=comment_content,
                comment_time=comment_time,
            )
            unit.save()
            return redirect(f"/movie/{movieId}")
        else:

            return render(request, "comment.html", locals())

    else:
        user = None
        admin = None
        mess = "請先登入"
        return render(request, "login.html", locals())


def show_fav(request):  # 我的最愛
    if "username" in request.session:
        user = request.session["username"]
        admin = request.session["admin"]
        try:
            fav_list = Favorite.objects.filter(
                fav_user=User.objects.get(acc=request.session["acc"])
            )
            total = len(fav_list)
            return render(request, "favorite.html", locals())
        except:
            mess = "查詢錯誤"
    else:
        mess = "請先登入"
        user = None
        admin = None
        return render(request, "login.html", locals())


def add_fav(request, movieId):
    if "acc" in request.session:
        try:

            exist = Favorite.objects.filter(
                fav_user=User.objects.get(acc=request.session["acc"]),
                fav_movie=Movie.objects.get(id=movieId),
            )

            exist = len(exist)

        except:
            exist = 0
        if exist == 0:
            unit = User.objects.get(acc=request.session["acc"]).fav_user_id.create(
                fav_user=request.session["acc"],
                fav_movie=Movie.objects.get(id=movieId),
                click_time=timezone.now(),
            )
            unit.save()
            return redirect(f"/movie/{movieId}")
        else:
            mess = "已經加入最愛"
            return redirect(f"/movie/{movieId}")
    else:
        mess = "請先登入"
        user = None
        admin = None
        return render(request, "login.html", locals())


def del_fav(request, movieId):
    if "acc" in request.session:
        try:
            unit = Favorite.objects.get(
                fav_user=User.objects.get(acc=request.session["acc"]),
                fav_movie=Movie.objects.get(id=movieId),
            )
            unit.delete()
            return redirect(show_fav)
        except:
            mess = "已經刪除"
            return render(request, "favorite.html", locals())
    else:
        mess = "請先登入"
        return render(request, "login.html", locals())


def update_theater(request):  # 暫時的，到時候跟電影資料上傳寫在一起
    Theater.objects.all().delete()
    datas = Show.objects.all()
    for data in datas:
        if "秀泰" in data.theater_name:
            if (
                len(
                    Theater.objects.filter(
                        name=data.theater_name.split("秀泰")[0] + "秀泰"
                    )
                )
                == 0
            ):
                Theater.objects.create(
                    name=data.theater_name.split("秀泰")[0] + "秀泰", place=data.place
                )
        else:
            if len(Theater.objects.filter(name=data.theater_name)) == 0:
                Theater.objects.create(name=data.theater_name, place=data.place)

    return HttpResponse("影院資料更新完成")


def show_theater_list(request):
    if "username" in request.session:
        user = request.session["username"]
        admin = request.session["admin"]
    else:
        user = None
        admin = None
    theater_north, theater_west, theater_east, theater_south = [], [], [], []
    for i in ["台北市", "新北市", "基隆市", "宜蘭縣", "桃園市", "新竹縣", "新竹市"]:
        theater_north += Theater.objects.filter(place__contains=i)
    for j in ["苗栗縣", "台中市", "彰化縣", "南投縣", "雲林縣"]:
        theater_west += Theater.objects.filter(place__contains=j)
    for k in ["花蓮縣", "台東縣"]:
        theater_east += Theater.objects.filter(place__contains=k)
    for l in ["嘉義縣", "嘉義市", "台南市", "高雄市", "屏東縣"]:
        theater_south += Theater.objects.filter(place__contains=l)
    theater_vs = Theater.objects.filter(name__contains="威秀")
    theater_st = Theater.objects.filter(name__contains="秀泰")
    theater_ab = Theater.objects.filter(name__contains="國賓")
    theater_mrm = Theater.objects.filter(name__contains="美麗華")
    theater_mrn = Theater.objects.filter(name__contains="美麗新")

    return render(request, "theaterList.html", locals())


def show_theater(request, theaterName):
    if "username" in request.session:
        user = request.session["username"]
        admin = request.session["admin"]
    else:
        user = None
        admin = None
    movie_obj = (
        Show.objects.filter(theater_name__contains=theaterName)
        .values_list("movie__title")
        .distinct()
    )
    movie_title = [movie[0] for movie in movie_obj]
    movie_playlist = [Movie.objects.get(title=movie) for movie in movie_title]
    theaterName = theaterName

    return render(request, "theater.html", locals())


# 電影類型分類
def show_type_list(request):
    if "username" in request.session:
        user = request.session["username"]
        admin = request.session["admin"]
    else:
        user = None
        admin = None
    type_list = []
    temp_type_list = Movie.objects.all().values_list("type").distinct()
    for type in temp_type_list:
        for t in type[0].split("、"):
            if "/" in t:
                for y in t.split("/"):
                    type_list.append(y)
            elif t == "":
                continue
            else:
                type_list.append(t)
    # print(type_list)
    type_list = list(set(type_list))
    type_list_pic = []
    # print("//////")
    for type in type_list:
        type_list_pic.append(
            [type, Movie.objects.filter(type__contains=type).order_by("?").first()]
        )
        # print(type)
    # print(type_list_pic)
    return render(request, "movieType.html", locals())


# 電影類型資料呈現
def show_type_movie(request, movieType):
    if "username" in request.session:
        user = request.session["username"]
        admin = request.session["admin"]
    else:
        user = None
        admin = None
    # '__contains':type欄位包含特定字段的資料
    movielist = Movie.objects.filter(type__contains=movieType)
    movieType = movieType
    return render(request, "typeShowMovie.html", locals())


def show_time(request, theaterName, movieName):
    if "username" in request.session:

        user = request.session["username"]
        admin = request.session["admin"]
    else:
        user = None
        admin = None
    movie_date = (
        Show.objects.filter(
            theater_name__contains=theaterName, movie=Movie.objects.get(title=movieName)
        )
        .values_list("date", "roomType")
        .distinct()
    )
    movie_showtime = Show.objects.filter(
        theater_name__contains=theaterName, movie=Movie.objects.get(title=movieName)
    )
    movie_obj = Movie.objects.get(title=movieName)
    return render(request, "theaterShow.html", locals())


def hot_movie(request):
    if "username" in request.session:
        user = request.session["username"]
        admin = request.session["admin"]
    else:
        user = None
        admin = None
    return render(request, "hot.html", locals())


# def pre(request):
#     if "username" in request.session:
#         user = request.session["username"]
#         fav_list = Favorite.objects.filter(
#             fav_user=User.objects.get(acc=request.session["acc"])
#         )
#         fav_list = [fav.fav_movie.title for fav in fav_list]
#         mov_list = Movie.objects.all()
#         templist = []
#         mov_dict = {}
#         for mov in mov_list:
#             for fav in fav_list:
#                 if fav == mov.title:
#                     templist.append(
#                         {
#                             "title": mov.title,
#                             "director": mov.director,
#                             "actors": mov.cast.strip("(配音)")
#                             .replace(",", "、")
#                             .split("、"),
#                             "genre": mov.type.replace("/", "、").split("、"),
#                             "liked": 1,
#                         }
#                     )

#                 else:
#                     templist.append(
#                         {
#                             "title": mov.title,
#                             "director": mov.director,
#                             "actors": mov.cast.strip("(配音)")
#                             .replace(",", "、")
#                             .split("、"),
#                             "genre": mov.type.replace("/", "、").split("、"),
#                             "liked": 0,
#                         }
#                     )
#                 break

#         # mov_dict = {"movies": templist}
#         # print(mov_dict)
#         # 使用者收藏的電影 (標示使用者喜愛的電影)
#         user_liked_movies = ["乒乓男孩", "台北追緝令"]

#         # Step 1: 建立特徵矩陣
#         all_genres = {genre for movie in templist for genre in movie["genre"]}
#         mlb_genres = MultiLabelBinarizer(classes=list(all_genres))

#         # SVM用
#         def extract_features(movie):
#             genre_vector = mlb_genres.fit_transform([movie["genre"]])[0]
#             director_vector = [hash(movie["director"]) % 1000]  # 將導演名稱雜湊化為數字
#             actors_vector = [
#                 sum([hash(actor) % 1000 for actor in movie["actors"]])
#             ]  # 將演員名轉換為數字和
#             return list(genre_vector) + director_vector + actors_vector

#         X = [extract_features(movie) for movie in templist]  # 特徵矩陣
#         y = [
#             1 if movie["title"] in user_liked_movies else 0 for movie in templist
#         ]  # 標籤 (1: 喜愛, 0: 不喜愛)

#         # Step 2: 將資料分成訓練集與測試集
#         X_train, X_test, y_train, y_test = train_test_split(
#             X, y, test_size=0.2, random_state=42
#         )

#         # Step 3: 使用 SVM 建立分類模型
#         model = svm.SVC(kernel="linear", probability=True)
#         model.fit(X_train, y_train)

#         # Step 4: 預測測試集的結果
#         y_pred = model.predict(X_test)
#         print("測試集準確率:", accuracy_score(y_test, y_pred))

#         # Step 5: 預測使用者可能感興趣的電影
#         def predict_movie_interest(movie):
#             features = extract_features(movie)
#             prediction = model.predict([features])[0]
#             probability = model.predict_proba([features])[0][1]
#             return prediction, probability

#         # 測試預測
#         test_movie = {
#             "title": "乒乓男孩",
#             "genre": ["勵志", "劇情", "運動"],
#             "director": "洪伯豪",
#             "actors": ["徐若瑄", "鄭人碩", "施名帥", "彭裕愷", "李星緯"],
#         }
#         pred, prob = predict_movie_interest(test_movie)
#         print(f"預測結果: {'感興趣' if pred == 1 else '不感興趣'}, 機率: {prob:.2f}")

#         return HttpResponse(templist)
#     else:
#         user = None
#         return HttpResponse(user)

# df = pd.read_json()


# def trigger_tasks(requst):
#     run_showtimes_task(repeat=Task.DAILY,repeat_until=None)
#     run_vieshow_task(repeat=Task.DAILY,repeat_until=None)
#     run_moramar_task(repeat=Task.DAILY,repeat_until=None)
#     run_miranewcinemas_task(repeat=Task.DAILY,repeat_until=None)
#     run_ambassador_task(repeat=Task.DAILY,repeat_until=None)
#     return HttpResponse("All task schedule")
