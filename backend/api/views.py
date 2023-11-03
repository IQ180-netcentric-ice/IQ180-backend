import json
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
import math
import random
import string
import redis
redis_client = redis.Redis(host="redis", port=6379, db=0)
# redis_client = redis.Redis(host="localhost", port=6379, db=0)


# from base.models import User, Detail
# from .serializers import UserSerializer, DetailSerializer
# from asgiref.sync import sync_to_async
# from adrf.decorators import api_view
# from django.db import transaction


# @api_view(['GET'])
# def getData(request):
#     person = User.objects.all()
#     serializer = UserSerializer(person, many=True)
#     return Response(serializer.data)


# @api_view(['POST'])
# def postData(request):
#     serializer = UserSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#     return Response(serializer.data)

@api_view(['POST'])
def create_room(request):
    data = request.data
    

    length = 6
    characters = string.ascii_letters + string.digits
    room_id = ''.join(random.choice(characters) for _ in range(length))

    time = data.get('time', '')
    numRound = data.get('numRound', '')
    username = data.get('username', '')

    room_data = {"time": time,
                 "numRound": numRound}

    response_data = {
        'username': username,
        'room_id': room_id,
        'time': time,
        'numRound': numRound,
        'message': f'Create room {room_id} success!'
    }
    player_data = {
                'role': 'Host',
                'username': username,
            }

    redis_key = f'players:{room_id}'
    redis_client.rpush(redis_key, json.dumps(room_data))
    redis_client.rpush(redis_key, json.dumps(player_data))

    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def join_room(request):
    data = request.data
    room_id = data.get('room_id', '')
    username = data.get('username', '')

    if not room_id:
        return Response({'error': 'Room ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    redis_key = f'players:{room_id}'
    players = redis_client.lrange(redis_key, 0, -1)

    if not players:
        return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

    player_data = [json.loads(player.decode('utf-8')) for player in players]

    num_round = ""
    room_time = ""

    for player in player_data:
        if 'numRound' in player:
            num_round = player['numRound']
        if 'time' in player:
            room_time = player['time']
    
    player_data = {
                'role': 'Guest',
                'username': username,
            }

    response_data = {
        'username': username,
        'room_id': room_id,
        'time': room_time,
        'numRound': num_round,
        'message': f'Join room {room_id} success!'
    }
    redis_client.rpush(redis_key, json.dumps(player_data))
    

    return Response(response_data, status=status.HTTP_200_OK)
