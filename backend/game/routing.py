from django.urls import re_path

from . import consumers

urlpatterns = [
    re_path(r'ws/game/(?P<room_id>\w+)/$', consumers.gameConsumer.as_asgi()),
]
