from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_room),
    path('join/', views.join_room),
    path('add/review/', views.addReview),
    path('reset/', views.reset_game, name='reset_game'),
    path('rooms/', views.room_list, name='room_list'),

]