import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import random
import math
import redis
import uuid

redis_client = redis.Redis(host="localhost", port=6379, db=0)
# redis_client = redis.Redis(host="redis", port=6379, db=0)


class gameConsumer(WebsocketConsumer):
    def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.redis_key = f'players:{self.room_id}'
            self.room_group_id = 'game_%s' % self.room_id
            self.player_id = None
            player_data = {
                'role': '',
                'username': '',
                'uuid': self.player_id
            }
            redis_key = f'players:{self.room_id}'
            redis_client.rpush(redis_key, json.dumps(player_data))

            async_to_sync(self.channel_layer.group_add)(
                self.room_group_id,
                self.channel_name
            )
            self.accept()
        except KeyError as key_error:
            print(f"Key error: {key_error}")
            self.close()

    def disconnect(self, close_code):
        try:
            print(f'{self.username} disconnect')
            self.sendonlinestatus(False, self.username)
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_id,
                self.channel_name,
            )
        except Exception as e:
            print(f"An unexpected error occurred during disconnect: {e}")

    def sendonlinestatus(self, boolean, username):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_id,
            {
                'type': 'sendonlinestatus2',
                'Online': boolean,
                'username': username
            }
        )

    def sendonlinestatus2(self, event):
        Online = event['Online']
        Username = event['username']
        self.send(text_data=json.dumps({
            'Online': Online,
            'Username': Username
        }))

    def gen_uuid(self, username):
        namespace = uuid.UUID('d3f9b041-3a92-4450-b7ea-85a76ae6fe14')
        return uuid.uuid5(namespace, username)

    def remove_player(self):
        try:
            redis_key = f'players:{self.room_id}'
            uuid_to_remove = self.player_id
            players = redis_client.lrange(redis_key, 0, -1)

            for player in players:
                player_data = json.loads(player.decode('utf-8'))
                player_uuid = player_data.get('uuid')
                if player_uuid == uuid_to_remove:
                    redis_client.lrem(redis_key, 0, player)
                    print(f'Removed UUID: {uuid_to_remove}')

            updated_players = redis_client.lrange(redis_key, 0, -1)
            for updated_player in updated_players:
                print(updated_player.decode('utf-8'))
        except Exception as e:
            print(f"An unexpected error occurred during player removal: {e}")

    def update_player_username(self, username):
        try:
            players = redis_client.lrange(self.redis_key, 0, -1)
            for player in players:
                player_data = json.loads(player.decode('utf-8'))
                player_uuid = player_data.get('uuid')
                if player_data['username'] == username:
                    self.remove_player()
                    self.player_id = player_data['uuid']
                    player_uuid = self.player_id
                    self.sendonlinestatus(True, username)
                    print(f'Reconnecting for {username}')
                    break
                elif player_uuid == None:
                    player_data['username'] = username
                    player_data['uuid'] = str(self.gen_uuid(username))
                    self.player_id = player_data['uuid']
                    redis_client.lset(self.redis_key, players.index(
                        player), json.dumps(player_data))
                    print(
                        f'Updated username for UUID {self.player_id} to {username}')
                    self.sendonlinestatus(True, username)
        except Exception as e:
            print(f"An unexpected error occurred during username update: {e}")

    def set_player_role(self, role):
        try:
            redis_key = f'players:{self.room_id}'
            players = redis_client.lrange(redis_key, 0, -1)
            for player in players:
                player_data = json.loads(player.decode('utf-8'))
                player_uuid = player_data.get('uuid')
                if player_uuid == self.player_id:
                    player_data['role'] = role
                    redis_client.lset(redis_key, players.index(
                        player), json.dumps(player_data))
                    print(f'Set role to {role} for UUID: {self.player_id}')
                    break
        except Exception as e:
            print(f"An unexpected error occurred during role update: {e}")

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')

            if message_type == 'game_data':
                self.receive_game_data(text_data_json)
            elif message_type == 'game_problem':
                self.receive_game_problem(text_data_json)
            elif message_type == 'game_answer':
                self.receive_game_answer(text_data_json)
            elif message_type == 'create_room':
                self.receive_create_room(text_data_json)
            elif message_type == 'join_room':
                self.receive_join_room(text_data_json)
            elif message_type == 'quit':
                self.sendonlinestatus(False, self.username)
                self.remove_player()
            else:
                print(f"Received unsupported message type: {message_type}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    def receive_create_room(self, text_data):
        try:
            text_data_json = text_data
            username = text_data_json['username']
            self.username = username
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_id,
                {
                    'type': 'create_room',
                    'username': username
                }
            )
            self.update_player_username(username)
            self.set_player_role('host')
        except:
            pass

    def receive_join_room(self, text_data):
        try:
            text_data_json = text_data
            username = text_data_json['username']
            self.username = username
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_id,
                {
                    'type': 'join_room',
                    'username': username,
                }
            )
            self.update_player_username(username)
            self.set_player_role('guest')
        except:
            pass

    def receive_game_data(self, text_data):
        try:
            text_data_json = text_data
            if 'player_data' in text_data_json:
                room_id = text_data_json['room_id']
                player_data = text_data_json['player_data']
                curr_round = text_data_json['curr_round']
                time_duration = text_data_json['time_duration']
                player_data = text_data_json['player_data']

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_id,
                    {
                        'type': 'game_data',
                        'room_id': room_id,
                        'curr_round': curr_round,
                        'time_duration': time_duration,
                        'player_data': player_data,
                    }
                )
            else:
                raise ValueError("'player_data' not found in JSON")
        except json.JSONDecodeError as json_error:
            print(f"JSON decoding error: {json_error}")
        except KeyError as key_error:
            print(f"Key error: {key_error}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def receive_game_problem(self, text_data):
        try:
            text_data_json = text_data
            if 'curr_round' in text_data_json:
                room_id = text_data_json['room_id']
                curr_round = text_data_json['curr_round']

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_id,
                    {
                        'type': 'game_problem',
                        'room_id': room_id,
                        'curr_round': curr_round,
                    }
                )
            else:
                raise ValueError("'game_round' not found in JSON")
        except json.JSONDecodeError as json_error:
            print(f"JSON decoding error: {json_error}")
        except KeyError as key_error:
            print(f"Key error: {key_error}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def receive_game_answer(self, text_data):
        try:
            text_data_json = text_data
            if 'curr_round' in text_data_json:
                room_id = text_data_json['room_id']
                curr_round = text_data_json['curr_round']
                problem = text_data_json['problem']
                player_answer = text_data_json['player_answer']

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_id,
                    {
                        'type': 'game_answer',
                        'room_id': room_id,
                        'curr_round': curr_round,
                        'problem': problem,
                        'player_answer': player_answer
                    }
                )
            else:
                raise ValueError("'game_round' not found in JSON")
        except json.JSONDecodeError as json_error:
            print(f"JSON decoding error: {json_error}")
        except KeyError as key_error:
            print(f"Key error: {key_error}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def create_room(self, event):
        try:
            if 'username' in event:
                username = event['username']
                room_id = self.room_id
                player_id = self.player_id
                self.send(text_data=json.dumps({
                    'type': 'create_room',
                    'room_id': room_id,
                    'host': username,
                    'uuid': player_id,
                    'status': True,
                    'message': 'Create room success!'
                }))
            else:
                raise ValueError("'player_data' not found in event")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def join_room(self, event):
        try:
            if 'username' in event:
                username = event['username']
                room_id = self.room_id
                player_id = self.player_id
                self.send(text_data=json.dumps({
                    'type': 'join_room',
                    'room_id': room_id,
                    'guest': username,
                    'uuid': player_id,
                    'status': True,
                    'message': f'Player {username} has joined room!'
                }))
            else:
                raise ValueError("'player_data' not found in event")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def game_data(self, event):
        try:
            if 'player_data' in event:
                room_id = event['room_id']
                curr_round = event['curr_round']
                time_duration = event['time_duration']
                player_data = event['player_data']
                self.send(text_data=json.dumps({
                    'type': 'game_data',
                    'room_id': room_id,
                    'curr_round': curr_round,
                    'time_duration': time_duration,
                    'player_data': player_data,
                }))
            else:
                raise ValueError("'player_data' not found in event")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def game_problem(self, event):
        try:
            if 'curr_round' in event:
                curr_round = event['curr_round']
                room_id = event['room_id']
                prob = []
                for num in range(5):
                    prob.append(random.randint(0, 9))
                self.send(text_data=json.dumps({
                    'type': 'game_problem',
                    'room_id': room_id,
                    'curr_round': curr_round,
                    'problem': prob,
                }))
            else:
                raise ValueError("'game_round' not found in event")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def evaluate_winner_round(self, ans1, ans2, prob):
        ans1 = int(ans1)
        ans2 = int(ans2)
        prob = int(prob)
        if math.fabs(ans1-prob) < math.fabs(ans2-prob):
            return 'player1'
        elif math.fabs(ans1-prob) > math.fabs(ans2-prob):
            return 'player2'
        else:
            return 'tied'

    def game_answer(self, event):
        try:
            if 'player_answer' in event:
                player_answer = event['player_answer']
                room_id = event['room_id']
                curr_round = event['curr_round']
                problem = event['problem']
                if player_answer['player1']['answer'] != "" and player_answer['player2']['answer'] != "":
                    print(player_answer['player2']['answer'] == "")
                    winner = self.evaluate_winner_round(
                        player_answer['player1']['answer'], player_answer['player2']['answer'], problem)
                    print(winner)
                    self.send(text_data=json.dumps({
                        'type': 'game_answer',
                        'room_id': room_id,
                        'curr_round': curr_round,
                        'problem': problem,
                        'winner': player_answer[winner]['uuid'],
                        'player_answer': player_answer[winner]['answer']
                    }))
                else:
                    self.send(text_data=json.dumps({
                        'type': 'game_answer',
                        'room_id': room_id,
                        'curr_round': curr_round,
                        'problem': problem,
                        'player_answer': player_answer
                    }))
                    raise ValueError("Need to submit one more answer")
            else:
                raise ValueError("'game_round' not found in event")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
