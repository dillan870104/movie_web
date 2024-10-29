"""
URL configuration for movie_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views   
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from movie_ticket_booking import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.movielist),
    path("index/", views.movielist),
    path("update/<str:cinemaName>", views.movie_update),
    path("update_theater/", views.update_theater),  # 暫時的
    path("delete/", views.del_show),  # 暫時的
    path("movie/<int:movieId>", views.show_movie_info),
    path("comment/<int:movieId>", views.leave_comment),
    path("register/", views.register),
    path("login/", views.login),
    path("logout/", views.logout),
    path("favorite/", views.show_fav),
    path("favorite/add/<int:movieId>", views.add_fav),
    path("favorite/del/<int:movieId>", views.del_fav),
    path("type/", views.show_type_list),
    path("type/<str:movieType>", views.show_type_movie),
    path("theater/", views.show_theater_list),
    path("theater/<str:theaterName>", views.show_theater),
    path("theater/<str:theaterName>/<str:movieName>", views.show_time),
    path("verify/", views.verify, name="verify"),
    path("check_ver/", views.check_ver),
]
