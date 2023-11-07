from .serializers import UserSerializer, ReviewSerializer
from base.models import User, Review
import json
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
import math
import random
import string
import redis
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import os
from dotenv import load_dotenv
from django.shortcuts import render
load_dotenv()


redis_client = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=0)



# from asgiref.sync import sync_to_async
# from adrf.decorators import api_view
# from django.db import transaction


# @api_view(['GET'])
# def getData(request):
#     person = User.objects.all()
#     serializer = UserSerializer(person, many=True)
#     return Response(serializer.data)


@api_view(['POST'])
def addReview(request):
    username = request.data.get('username')
    review = request.data.get('review')
    star = request.data.get('star')
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        user, created = User.objects.get_or_create(username=username)

        response_data = {
            'username': username,
            'review': review,
            'star': star,
            'message': 'Create review success'
        }
        serializer.save(user=user)
        return Response(response_data,status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

@api_view(['POST'])
def reset_game(request):
    data = request.data
    channel_layer = get_channel_layer()
    room_id = request.data.get('room_id')
    room_group_id = 'game_%s' % room_id

    async_to_sync(channel_layer.group_send)(
        room_group_id,
        {
            'type': 'game_reset',
            'message': 'The game has been reset.'
        }
    )

    return JsonResponse({'message': 'Game room reset successfully'})

def room_list(request):

    room_ids = redis_client.keys("players:*")
    active_rooms = [room_id.decode("utf-8").split(":")[1] for room_id in room_ids]
    
    
    

    return render(request, 'room_list.html', {'active_rooms': active_rooms})

