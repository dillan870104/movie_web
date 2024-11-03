from django.contrib import admin
from movie_ticket_booking.models import (
    User,
    Movie,
    Show,
    TextBoard,
    Favorite,
    Theater,
)  # model的匯入資料庫


# Register your models here.
class userAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "acc",
        "pwd",
        "email",
        "username",
        "registerdate",
        "tel",
        "admin_id",
    )


class movieAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "title_en",
        "time",
        "img_src",
        "release_date",
        "type",
        "director",
        "cast",
        "assignment",
        "level",
    )


class showAdmin(admin.ModelAdmin):
    list_display = (
        "movie",
        "date",
        "roomType",
        "theater_name",
        "playTime",
        "place",
    )


class textBoardAdmin(admin.ModelAdmin):
    list_display = (
        "tb_movie",
        "tb_user",
        "content",
        "comment_time",
    )


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "fav_user",
        "fav_movie",
        "click_time",
    )


class TheaterAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "place",
    )


admin.site.register(User, userAdmin)
admin.site.register(Movie, movieAdmin)
admin.site.register(Show, showAdmin)
admin.site.register(TextBoard, textBoardAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Theater, TheaterAdmin)
