from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_room),
    path('join/', views.join_room),
    path('add/review', views.addReview),
    # # path('adduserdata', views.addData),
]