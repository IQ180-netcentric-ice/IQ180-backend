from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_room),
    path('join/', views.join_room)
    # path('adduser', views.postData),
    # # path('adduserdata', views.addData),
]