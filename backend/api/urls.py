from django.urls import path
from . import views

urlpatterns = [
    path('roomid/', views.getRoomId),
    # path('adduser', views.postData),
    # # path('adduserdata', views.addData),
]