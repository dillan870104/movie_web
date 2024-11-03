from django.db import models


# Create your models here.
class User(models.Model):
    # uid = models.AutoField(primary_key=True, default=0)
    acc = models.CharField(max_length=20, null=False, unique=True)
    pwd = models.CharField(max_length=20, null=False)
    email = models.EmailField(max_length=50, null=False, unique=True)
    username = models.CharField(max_length=20, null=False)
    registerdate = models.DateTimeField()
    tel = models.CharField(max_length=10)
    admin_id = models.BooleanField(default=False)
    # profile_pic = models.ImageField(upload_to="static/images")

    class Meta:
        db_table = "User"


# 電影模型
class Movie(models.Model):
    title = models.CharField(max_length=40, null=False)
    title_en = models.CharField(max_length=50)
    time = models.CharField(max_length=10)
    img_src = models.CharField(max_length=100)
    release_date = models.DateField()
    type = models.CharField(max_length=20)
    director = models.CharField(max_length=40)
    cast = models.CharField(max_length=100)
    assignment = models.CharField(max_length=500)
    level = models.CharField(max_length=10)

    class Meta:
        db_table = "db_movie"


# 場次模型
class Show(models.Model):
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="theater_movie"
    )
    roomType = models.CharField(max_length=20)
    date = models.DateField()
    playTime = models.CharField(max_length=20)
    theater_name = models.CharField(max_length=40, null=False)

    place = models.CharField(max_length=40, null=False)
    # available_seats = models.IntegerField()

    class Meta:
        db_table = "db_show"


# 留言板模型
class TextBoard(models.Model):
    tb_movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="text_movie"
    )
    tb_user = models.CharField(max_length=20, null=False)
    content = models.CharField(max_length=500)
    comment_time = models.DateTimeField()

    class Meta:
        db_table = "db_comment"


# 留言板模型
class Favorite(models.Model):
    fav_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="fav_user_id"
    )
    fav_movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="fav_movie_id"
    )

    click_time = models.DateTimeField()

    class Meta:
        db_table = "db_favorite"


# 電影院模型
class Theater(models.Model):
    name = models.CharField(max_length=40, null=False)
    place = models.CharField(max_length=40, null=False)

    class Meta:
        db_table = "db_theater"
