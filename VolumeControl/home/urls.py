from django.contrib import admin
from django.urls import path,include
from home import urls
from home import views

urlpatterns = [
    path('', views.index, name = "home"),
    path('volume_control', views.volume_control, name = "volume_control"),
    path('about_us', views.about_us, name = "about_us"),
]
