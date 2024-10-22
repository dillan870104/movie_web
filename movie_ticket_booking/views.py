from django.shortcuts import render, redirect
from django.http import HttpResponse
from movie_ticket_booking.models import User, Movie, Show, TextBoard, Favorite, Theater
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from movie_ticket_booking.form import RegisterForm
import random

# Create your views here.


def movie_update(request, cinemaName):  # 所有電影清單更新在這
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
                    type=vieshow_movie[8],
                    director=vieshow_movie[6],
                    cast=vieshow_movie[7],
                    assignment=vieshow_movie[9],
                    level=vieshow_movie[14],
                )
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
                    img_src="N/A",
                    release_date=showtime_movie["上映日"],
                    type=showtime_movie["類型"],
                    director=showtime_movie["導演"],
                    cast=showtime_movie["演員"],
                    assignment=showtime_movie["簡介"],
                    level=showtime_movie["級別"],
                )
            # 存進show資料表
            Movie.objects.get(
                title=showtime_movie["中文片名"],
            ).theater_movie.create(
                date=showtime_movie["日期"],
                roomType=showtime_movie["播放種類"],
                playTime=showtime_movie["時間"],
                theater_name=showtime_movie["影廳"],
                place=showtime_movie["影院位置"],
            )

    return HttpResponse("電影資料更新完成")


def movielist(request):
    try:
        movielist = Movie.objects.all()
        user = request.session["username"]
        return render(request, "home.html", locals())
    except:
        movielist = Movie.objects.all()
        user = None
        return render(request, "home.html", locals())


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
    return "fin"


def register(request):
    if request.method == "POST":
        postform = RegisterForm(request.POST)
        if postform.is_valid():
            username = postform.cleaned_data["username"]
            acc = postform.cleaned_data["acc"]
            pwd = postform.cleaned_data["pwd"]
            email = postform.cleaned_data["email"]

            tel = postform.cleaned_data["tel"]
            registerdate = timezone.now()
            try:
                user_img = postform.cleaned_data["user_img"]
            except:
                user_img = None
            finally:
                verify = ""  # 6位數驗證碼
                for i in range(6):
                    digi = random.randint(0, 9)
                    verify += str(digi)
                unit = User.objects.create(
                    username=username,
                    acc=acc,
                    pwd=pwd,
                    email=email,
                    tel=tel,
                    registerdate=registerdate,
                    profile_pic=user_img,
                    verify_code=verify,
                )

                unit.save()
                request.session["email"] = email

                # user = None
                return redirect("/verify/")
                # return render(request, "verify.html", locals())

    else:

        user = None
        postform = RegisterForm()
    return render(request, "register.html", locals())


def verify(request):
    # send_verify(email, verify)
    if "email" in request.session:
        email = request.session["email"]
        db_data = User.objects.get(email=email)
        registerdate = db_data.registerdate
        print(registerdate)
        now = timezone.now()
        print(now)
        print(now - registerdate)
        user = None

        try:
            v_code = request.POST["v_code"]

        except:
            v_code = "N/A"

        return render(request, "verify.html", locals())
    else:
        return render(request, "verify.html", locals())


def login(request):
    user = None
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
                return redirect("/index/")
            elif db_data.pwd != pwd:
                mess = "密碼錯誤"
                user = None
                return render(request, "login.html", locals())
            else:
                mess = "錯誤，請重新輸入"
                user = None
                return render(request, "login.html", locals())
        except:
            mess = "沒有此帳號，請重新輸入"
            user = None
            return render(request, "login.html", locals())

    else:
        user = None
        return render(request, "login.html", locals())


def logout(request):

    request.session.clear()

    return redirect("/index/")


def show_movie_info(request, movieId):
    try:
        if "username" in request.session:
            movieId = movieId
            movie_info = Movie.objects.filter(id=movieId)
            show_list = Show.objects.filter(movie_id=movieId)
            text_info = TextBoard.objects.filter(tb_movie_id=movieId)
            user = request.session["username"]
            return render(request, "movie_info.html", locals())
        else:
            user = None
            movieId = movieId
            movie_info = Movie.objects.filter(id=movieId)
            show_list = Show.objects.filter(movie_id=movieId)
            text_info = TextBoard.objects.filter(tb_movie_id=movieId)
            return render(request, "movie_info.html", locals())
    except:
        return redirect("/index/")


def leave_comment(request, movieId):  # 留言板功能
    movie_info = Movie.objects.filter(id=movieId)
    if "username" in request.session:
        user = request.session["username"]
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
        mess = "請先登入"
        return render(request, "login.html", locals())


def show_fav(request):  # 我的最愛
    if "username" in request.session:
        user = request.session["username"]
        try:
            fav_list = Favorite.objects.filter(
                fav_user=User.objects.get(acc=request.session["acc"])
            )
            return render(request, "favorite.html", locals())
        except:
            mess = "查詢錯誤"
    else:
        mess = "請先登入"
        user = None
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
    datas = Show.objects.all()
    for data in datas:
        if len(Theater.objects.filter(name=data.theater_name)) == 0:
            Theater.objects.create(name=data.theater_name, place=data.place)
    return HttpResponse("影院資料更新完成")


def show_theater_list(request):
    if "username" in request.session:
        user = request.session["username"]
        theater_list = Theater.objects.all()
        return render(request, "theaterList.html", locals())
    else:
        user = None
        theater_list = Theater.objects.all()
        return render(request, "theaterList.html", locals())


def show_theater(request, theaterName):
    if "username" in request.session:
        user = request.session["username"]
        movie_title = (
            Show.objects.filter(theater_name=theaterName)
            .values_list("movie__title")
            .distinct()
        )
        movie_title = [movie[0] for movie in movie_title]

        return render(request, "theater.html", locals())
    else:
        user = None
        movie_title = (
            Show.objects.filter(theater_name=theaterName)
            .values_list("movie__title")
            .distinct()
        )
        movie_title = [movie[0] for movie in movie_title]
        theaterName = theaterName
        return render(request, "theater.html", locals())


def show_time(request, theaterName, movieName):
    if "username" in request.session:
        user = request.session["username"]
        movie_date = (
            Show.objects.filter(
                theater_name=theaterName, movie=Movie.objects.get(title=movieName)
            )
            .values_list("date", "roomType")
            .distinct()
        )
        movie_showtime = Show.objects.filter(
            theater_name=theaterName, movie=Movie.objects.get(title=movieName)
        )
        return render(request, "theaterShow.html", locals())
    else:
        user = None
        movie_date = (
            Show.objects.filter(
                theater_name=theaterName, movie=Movie.objects.get(title=movieName)
            )
            .values_list("date", "roomType")
            .distinct()
        )
        movie_showtime = Show.objects.filter(
            theater_name=theaterName, movie=Movie.objects.get(title=movieName)
        )
        return render(request, "theaterShow.html", locals())
