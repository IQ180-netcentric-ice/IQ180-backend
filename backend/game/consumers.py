import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import random
import math
import redis
import uuid
from .numberSolver import Solve, OneFromTheTop, OneOfTheOthers
import re
import os
from dotenv import load_dotenv
load_dotenv()

redis_client = redis.Redis(host=os.getenv(
    'REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=0)


class gameConsumer(WebsocketConsumer):
    # session_seeds = {}
    # def start_game_session(self, room_id):
    #     seed = random.randint(0, 1000)
    #     self.session_seeds[room_id] = seed
    #     return seed

    def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.redis_key = f'players:{self.room_id}'
            self.room_group_id = 'game_%s' % self.room_id
            # self.player_id = None
            # player_data = {
            #     'role': '',
            #     'username': '',
            #     'uuid': self.player_id
            # }
            # redis_key = f'players:{self.room_id}'
            # redis_client.rpush(redis_key, json.dumps(player_data))

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
            # print(f'{self.username} disconnect')
            # self.sendonlinestatus(False, self.username)
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
        # Online = event['Online']
        # Username = event['username']
        redis_key = f'players:{self.room_id}'
        players = redis_client.lrange(redis_key, 0, -1)
        usernames = [json.loads(player.decode('utf-8'))['username']
                     for player in players]

        num_users = len(usernames)
        # self.send(text_data=json.dumps({
        #     'number_users': num_users,
        #     'users': usernames
        # }))

    def gen_uuid(self, username):
        namespace = uuid.UUID('d3f9b041-3a92-4450-b7ea-85a76ae6fe14')
        return uuid.uuid5(namespace, username)

    # def remove_player(self):
    #     try:
    #         redis_key = f'players:{self.room_id}'
    #         uuid_to_remove = self.player_id
    #         players = redis_client.lrange(redis_key, 0, -1)

    #         for player in players:
    #             player_data = json.loads(player.decode('utf-8'))
    #             player_uuid = player_data.get('uuid')
    #             if player_uuid == uuid_to_remove:
    #                 redis_client.lrem(redis_key, 0, player)
    #                 print(f'Removed UUID: {uuid_to_remove}')

    #         updated_players = redis_client.lrange(redis_key, 0, -1)
    #         for updated_player in updated_players:
    #             print(updated_player.decode('utf-8'))
    #     except Exception as e:
    #         print(f"An unexpected error occurred during player removal: {e}")

    # def update_player_username(self, username):
    #     try:
    #         players = redis_client.lrange(self.redis_key, 0, -1)
    #         for player in players:
    #             player_data = json.loads(player.decode('utf-8'))
    #             player_uuid = player_data.get('uuid')
    #             if player_data['username'] == username:
    #                 self.remove_player()
    #                 self.player_id = player_data['uuid']
    #                 player_uuid = self.player_id
    #                 # self.sendonlinestatus(True, username)
    #                 print(f'Reconnecting for {username}')
    #                 break
    #             elif player_uuid == None:
    #                 player_data['username'] = username
    #                 player_data['uuid'] = str(self.gen_uuid(username))
    #                 self.player_id = player_data['uuid']
    #                 redis_client.lset(self.redis_key, players.index(
    #                     player), json.dumps(player_data))
    #                 print(
    #                     f'Updated username for UUID {self.player_id} to {username}')
    #                 # self.sendonlinestatus(True, username)
    #     except Exception as e:
    #         print(f"An unexpected error occurred during username update: {e}")

    # def set_player_role(self, role):
    #     try:
    #         redis_key = f'players:{self.room_id}'
    #         players = redis_client.lrange(redis_key, 0, -1)
    #         for player in players:
    #             player_data = json.loads(player.decode('utf-8'))
    #             player_uuid = player_data.get('uuid')
    #             if player_uuid == self.player_id:
    #                 player_data['role'] = role
    #                 redis_client.lset(redis_key, players.index(
    #                     player), json.dumps(player_data))
    #                 print(f'Set role to {role} for UUID: {self.player_id}')
    #                 break
    #     except Exception as e:
    #         print(f"An unexpected error occurred during role update: {e}")

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')

            if message_type == 'game_data':
                self.receive_game_data(text_data_json)
            elif message_type == 'game_problem':
                self.receive_game_problem(text_data_json)
            elif message_type == 'game_hard_problem':
                self.receive_game_hard_problem(text_data_json)
            elif message_type == 'online_status':
                self.receive_online_status(text_data_json)
            elif message_type == 'ready_status':
                self.receive_ready_status(text_data_json)
            elif message_type == 'game_answer':
                self.receive_game_answer(text_data_json)
            elif message_type == 'create_room':
                self.receive_create_room(text_data_json)
            elif message_type == 'join_room':
                self.receive_join_room(text_data_json)
            elif message_type == 'quit':
                self.receive_quit(text_data_json)
            elif message_type == 'First_round':
                self.receive_firstround(text_data_json)
                # self.sendonlinestatus(False, self.username)
                # self.remove_player()
            else:
                print(f"Received unsupported message type: {message_type}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    # def receive_create_room(self, text_data):
    #     try:
    #         text_data_json = text_data
    #         username = text_data_json['username']
    #         self.username = username
    #         async_to_sync(self.channel_layer.group_send)(
    #             self.room_group_id,
    #             {
    #                 'type': 'create_room',
    #                 'username': username
    #             }
    #         )
    #         # self.sendonlinestatus(True, username)
    #         self.update_player_username(username)
    #         self.set_player_role('host')
    #     except:
    #         pass

    # def receive_join_room(self, text_data):
    #     try:
    #         text_data_json = text_data
    #         username = text_data_json['username']
    #         self.username = username
    #         async_to_sync(self.channel_layer.group_send)(
    #             self.room_group_id,
    #             {
    #                 'type': 'join_room',
    #                 'username': username,
    #             }
    #         )
    #         # self.sendonlinestatus(True, username)
    #         self.update_player_username(username)
    #         self.set_player_role('guest')
    #     except:
    #         pass

    def receive_ready_status(self, text_data):
        try:
            text_data_json = text_data
            if 'player_status' in text_data_json:
                room_id = self.room_id
                player_status = text_data_json['player_status']

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_id,
                    {
                        'type': 'ready_status',
                        'room_id': room_id,
                        'player_status': player_status
                    }
                )
            else:
                raise ValueError("'player_status' not found in JSON")
        except json.JSONDecodeError as json_error:
            print(f"JSON decoding error: {json_error}")
        except KeyError as key_error:
            print(f"Key error: {key_error}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def receive_online_status(self, text_data):
        try:
            text_data_json = text_data

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_id,
                {
                    'type': 'online_status',
                }
            )
        except json.JSONDecodeError as json_error:
            print(f"JSON decoding error: {json_error}")
        except KeyError as key_error:
            print(f"Key error: {key_error}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def receive_quit(self, text_data):
        try:
            text_data_json = text_data
            username = text_data_json['username']

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_id,
                {
                    'type': 'quit',
                    'username': username
                }
            )
        except json.JSONDecodeError as json_error:
            print(f"JSON decoding error: {json_error}")
        except KeyError as key_error:
            print(f"Key error: {key_error}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def receive_game_data(self, text_data):
        try:
            text_data_json = text_data
            room_id = self.room_id
            redis_key = f'players:{self.room_id}'
            players = redis_client.lrange(redis_key, 0, -1)
            numround = [json.loads(player.decode('utf-8')).get('numRound', '')
                        for player in players if 'numRound' in json.loads(player.decode('utf-8'))][0]
            timeduration = [json.loads(player.decode('utf-8')).get('time', '')
                            for player in players if 'time' in json.loads(player.decode('utf-8'))][0]
            if 'player_data' in text_data_json:
                room_id = self.room_id
                player_data = text_data_json['player_data']
                curr_round = text_data_json['curr_round']
                # time_duration = text_data_json['time_duration']
                player_data = text_data_json['player_data']

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_id,
                    {
                        'type': 'game_data',
                        'room_id': room_id,
                        'curr_round': curr_round,
                        'numround': numround,
                        'timeduration': timeduration,
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

    # def receive_game_hard_problem(self, text_data):
    #     try:
    #         text_data_json = text_data
    #         if 'curr_round' in text_data_json:
    #             room_id = self.room_id
    #             curr_round = text_data_json['curr_round']

    #             async_to_sync(self.channel_layer.group_send)(
    #                 self.room_group_id,
    #                 {
    #                     'type': 'game_hard_problem',
    #                     'room_id': room_id,
    #                     'curr_round': curr_round,
    #                 }
    #             )
    #         else:
    #             raise ValueError("'game_round' not found in JSON")
    #     except json.JSONDecodeError as json_error:
    #         print(f"JSON decoding error: {json_error}")
    #     except KeyError as key_error:
    #         print(f"Key error: {key_error}")
    #     except Exception as e:
    #         print(f"An unexpected error occurred: {e}")

    def receive_game_problem(self, text_data):
        try:
            room_id = self.room_id
            redis_key = f'players:{self.room_id}'
            players = redis_client.lrange(redis_key, 0, -1)
            numround = [json.loads(player.decode('utf-8')).get('numRound', '')
                        for player in players if 'numRound' in json.loads(player.decode('utf-8'))][0]
            timeduration = [json.loads(player.decode('utf-8')).get('time', '')
                            for player in players if 'time' in json.loads(player.decode('utf-8'))][0]
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_id,
                {
                    'type': 'game_problem',
                    'room_id': room_id,
                    'numRound': numround,
                    'timeduration': timeduration
                }
            )

        except json.JSONDecodeError as json_error:
            print(f"JSON decoding error: {json_error}")
        except KeyError as key_error:
            print(f"Key error: {key_error}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def receive_game_hard_problem(self, text_data):
        try:
            room_id = self.room_id
            redis_key = f'players:{self.room_id}'
            players = redis_client.lrange(redis_key, 0, -1)
            numround = [json.loads(player.decode('utf-8')).get('numRound', '')
                        for player in players if 'numRound' in json.loads(player.decode('utf-8'))][0]
            timeduration = [json.loads(player.decode('utf-8')).get('time', '')
                            for player in players if 'time' in json.loads(player.decode('utf-8'))][0]
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_id,
                {
                    'type': 'game_hard_problem',
                    'room_id': room_id,
                    'numRound': numround,
                    'timeduration': timeduration
                }
            )

        except json.JSONDecodeError as json_error:
            print(f"JSON decoding error: {json_error}")
        except KeyError as key_error:
            print(f"Key error: {key_error}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def receive_game_answer(self, text_data):
        try:
            text_data_json = text_data
            room_id = self.room_id
            redis_key = f'players:{self.room_id}'
            players = redis_client.lrange(redis_key, 0, -1)
            numround = [json.loads(player.decode('utf-8')).get('numRound', '')
                        for player in players if 'numRound' in json.loads(player.decode('utf-8'))][0]
            timeduration = [json.loads(player.decode('utf-8')).get('time', '')
                            for player in players if 'time' in json.loads(player.decode('utf-8'))][0]
            if 'curr_round' in text_data_json:
                room_id = self.room_id
                curr_round = text_data_json['curr_round']
                problem = text_data_json['problem']
                player_answer = text_data_json['player_answer']

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_id,
                    {
                        'type': 'game_answer',
                        'room_id': room_id,
                        'curr_round': curr_round,
                        'numround': numround,
                        "timeduration": timeduration,
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

    # def create_room(self, event):
    #     try:
    #         if 'username' in event:
    #             username = event['username']
    #             room_id = self.room_id
    #             player_id = self.player_id
    #             self.send(text_data=json.dumps({
    #                 'type': 'create_room',
    #                 'room_id': room_id,
    #                 'host': username,
    #                 'uuid': player_id,
    #                 'status': True,
    #                 'message': 'Create room success!'
    #             }))
    #         else:
    #             raise ValueError("'player_data' not found in event")
    #     except Exception as e:
    #         print(f"An unexpected error occurred: {e}")

    # def join_room(self, event):
    #     try:
    #         if 'username' in event:
    #             username = event['username']
    #             room_id = self.room_id
    #             player_id = self.player_id
    #             self.send(text_data=json.dumps({
    #                 'type': 'join_room',
    #                 'room_id': room_id,
    #                 'guest': username,
    #                 'uuid': player_id,
    #                 'status': True,
    #                 'message': f'Player {username} has joined room!'
    #             }))
    #         else:
    #             raise ValueError("'player_data' not found in event")
    #     except Exception as e:
    #         print(f"An unexpected error occurred: {e}")

    def receive_firstround(self, text_data):
        try:
            text_data_json = text_data
            room_id = self.room_id
            redis_key = f'players:{self.room_id}'
            players = redis_client.lrange(redis_key, 0, -1)
            usernames = [json.loads(player.decode('utf-8')).get('username', '')
                         for player in players if 'username' in json.loads(player.decode('utf-8'))]
            timeduration = [json.loads(player.decode('utf-8')).get('time', '')
                            for player in players if 'time' in json.loads(player.decode('utf-8'))][0]
            numround = [json.loads(player.decode('utf-8')).get('numRound', '')
                        for player in players if 'numRound' in json.loads(player.decode('utf-8'))][0]
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_id,
                {
                    'type': 'first_round',
                    'room_id': self.room_id,
                    'time': timeduration,
                    'numRound': numround,
                    'p1': usernames[0],
                    'p2': usernames[1]
                }
            )

        except json.JSONDecodeError as json_error:
            print(f"JSON decoding error: {json_error}")
        except KeyError as key_error:
            print(f"Key error: {key_error}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def ready_status(self, event):
        try:
            if 'player_status' in event:
                room_id = event['room_id']
                player_status = event['player_status']
                self.send(text_data=json.dumps({
                    'type': 'player_status',
                    'room_id': room_id,
                    'player_status': player_status
                }))
            else:
                raise ValueError("'player_data' not found in event")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def online_status(self, event):
        try:
            redis_key = f'players:{self.room_id}'
            players = redis_client.lrange(redis_key, 0, -1)
            usernames = [json.loads(player.decode('utf-8')).get('username', '')
                         for player in players if 'username' in json.loads(player.decode('utf-8'))]

            num_users = len(usernames)

            self.send(text_data=json.dumps({
                'type': 'player_status',
                'room_id': self.room_id,
                'number_of_users': num_users,
                'players': usernames
            }))
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def quit(self, event):
        try:
            redis_key = f'players:{self.room_id}'
            username_to_remove = event['username']
            players = redis_client.lrange(redis_key, 0, -1)

            for player in players:
                player_data = json.loads(player.decode('utf-8'))
                player_username = player_data.get('username')
                if player_username == username_to_remove:
                    redis_client.lrem(redis_key, 0, player)
                    # self.remove_player(redis_key, player)
                    print(f'Removed player: {username_to_remove}')
                    self.process_player_list(redis_key)

            # usernames = [json.loads(player.decode('utf-8')).get('username', '')
            #              for player in players if 'username' in json.loads(player.decode('utf-8'))]
            # num_users = len(usernames)
            # self.send(text_data=json.dumps({
            #     'type': 'player_status',
            #     'room_id': self.room_id,
            #     'number_of_users': num_users,
            #     'players': usernames
            # }))
        except Exception as e:
            print(f"An unexpected error occurred during player removal: {e}")

    def process_player_list(self, redis_key):
        players = redis_client.lrange(redis_key, 0, -1)
        usernames = [json.loads(player.decode('utf-8')).get('username', '')
                     for player in players if 'username' in json.loads(player.decode('utf-8'))]
        num_users = len(usernames)
        self.send(text_data=json.dumps({
            'type': 'player_status',
            'room_id': self.room_id,
            'number_of_users': num_users,
            'players': usernames
        }))

    def game_data(self, event):
        try:
            if 'player_data' in event:
                # redis_key = f'players:{self.room_id}'
                # players = redis_client.lrange(redis_key, 0, -1)
                # numround = [json.loads(player.decode('utf-8')).get('numRound', '')
                #             for player in players if 'numRound' in json.loads(player.decode('utf-8'))][0]
                curr_round = event['curr_round']
                time_duration = event['timeduration']
                player_data = event['player_data']
                numround = event['numround']
                self.send(text_data=json.dumps({
                    'type': 'game_data',
                    'room_id': self.room_id,
                    'curr_round': curr_round,
                    'numRound': numround,
                    'time_duration': time_duration,
                    'player_data': player_data,
                }))
            else:
                raise ValueError("'player_data' not found in event")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def first_round(self, event):

        combined_seed = self.room_id
        random.seed(combined_seed)

        num = random.randint(0, 1)
        if num == 0:
            start = False
            end = True
        elif num == 1:
            start = True
            end = False
        try:
            room_id = self.room_id
            p1 = event['p1']
            p2 = event['p2']
            time_duration = event['time']
            numround = event['numRound']
            self.send(text_data=json.dumps({
                'type': 'first_round',
                'room_id': room_id,
                'curr_round': 1,
                'time_duration': time_duration,
                'numRound': numround,
                'player_data': {
                    "p1": {
                        "username": p1,
                        "score": 0,
                        "turn": start
                    },
                    "p2": {
                        "username": p2,
                        "score": 0,
                        "turn": end
                    }
                }
            }))
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def extract_hint(self, full_solution):
        operators = re.findall(r'[+\-*/]', full_solution)

        operator_descriptions = {
            '+': 'Addition',
            '-': 'Subtraction',
            '*': 'Multiplication',
            '/': 'Division',
        }
        hint = [operator_descriptions[operator] for operator in operators]
        hint_str = ', '.join(hint)

        return hint_str

    def generate_problem(self, numRound):
        a = []
        for i in (range(numRound)):
            b = dict()
            combined_seed = f"{self.room_id}_{i}"
            random.seed(combined_seed)
            # set_seed(combined_seed)
            # print('consumer', combined_seed)

            def OneFromTheTop():
                return random.choice([1, 2, 3])

            def OneOfTheOthers(numbers=[]):
                if not numbers:
                    numbers = random.sample(range(4, 10), 4)
                return numbers.pop()

            # target = random.randint(100, 200)
            # other_numbers = random.sample(range(1, 11), 4)
            # numbers = [OneFromTheTop()] + [OneOfTheOthers(other_numbers)
            #                             for i in range(4)]
            # solution = Solve(target, numbers)

            while True:
                target = random.randint(100, 200)
                other_numbers = random.sample(range(4, 10), 4)
                numbers = [OneFromTheTop()] + [OneOfTheOthers(other_numbers)
                                               for i in range(4)]
                solution = Solve(target, numbers)
                while solution and len(solution.split()) < 8:
                    target = random.randint(100, 200)
                    other_numbers = random.sample(range(4, 10), 4)
                    numbers = [OneFromTheTop()] + [OneOfTheOthers(other_numbers)
                                                   for i in range(4)]
                    print(len(solution.split()))
                    print(solution)
                    solution = Solve(target, numbers)
                if solution is not None:
                    break

            hint = self.extract_hint(str(solution))
            b["target"] = target
            b["problem"] = numbers
            b["solution"] = solution
            b["hint"] = hint
            a += [b]
        return a

    def generate_hard_problem(self, numRound):
        a = []
        for i in (range(numRound)):
            b = dict()
            combined_seed = f"{self.room_id}_{i}"
            random.seed(combined_seed)
            # set_seed(combined_seed)
            # print('consumer', combined_seed)

            def OneFromTheTop():
                return random.choice([100, 150, 200])

            def OneOfTheOthers(numbers=[]):
                if not numbers:
                    numbers = random.sample(range(50, 100), 4)
                return numbers.pop()

            # target = random.randint(100, 200)
            # other_numbers = random.sample(range(1, 11), 4)
            # numbers = [OneFromTheTop()] + [OneOfTheOthers(other_numbers)
            #                             for i in range(4)]
            # solution = Solve(target, numbers)

            while True:
                target = random.randint(500, 1000)
                other_numbers = random.sample(range(50, 100), 4)
                numbers = [OneFromTheTop()] + [OneOfTheOthers(other_numbers)
                                               for i in range(4)]
                solution = Solve(target, numbers)
                while solution and len(solution.split()) < 8:
                    target = random.randint(500, 1000)
                    other_numbers = random.sample(range(50, 100), 4)
                    numbers = [OneFromTheTop()] + [OneOfTheOthers(other_numbers)
                                                   for i in range(4)]
                    print(len(solution.split()))
                    print(solution)
                    solution = Solve(target, numbers)
                if solution is not None:
                    break

            hint = self.extract_hint(str(solution))
            b["target"] = target
            b["problem"] = numbers
            b["solution"] = solution
            b["hint"] = hint
            a += [b]
        return a

    # def game_problem(self, event):
    #     try:
    #         if 'curr_round' in event:
    #             curr_round = event['curr_round']
    #             room_id = event['room_id']

    #             while True:
    #                 target = random.randint(100, 200)
    #                 numbers = [OneFromTheTop()] + [OneOfTheOthers()
    #                                                for i in range(4)]
    #                 solution = Solve(target, numbers)
    #                 while solution and len(solution.split()) < 8:
    #                     target = random.randint(100, 200)
    #                     numbers = [OneFromTheTop()] + [OneOfTheOthers()
    #                                                    for i in range(4)]
    #                     print(len(solution.split()))
    #                     print(solution)
    #                     solution = Solve(target, numbers)
    #                 if solution is not None:
    #                     break

    #             # print(str(solution))
    #             hint = self.extract_hint(str(solution))

    #             self.send(text_data=json.dumps({
    #                 'type': 'game_problem',
    #                 'room_id': room_id,
    #                 'curr_round': curr_round,
    #                 'target': target,
    #                 'problem': numbers,
    #                 'solution': solution,
    #                 'hint': hint
    #             }))
    #         else:
    #             raise ValueError("'curr_round' not found in event")
    #     except Exception as e:
    #         print(f"An unexpected error occurred: {e}")

    def game_problem(self, event):
        try:
            numRound = event['numRound']
            room_id = event['room_id']
            timeduration = event['timeduration']
            problem_data = self.generate_problem(numRound)
            self.send(text_data=json.dumps({
                'type': 'game_problem',
                'room_id': room_id,
                'timeduration': timeduration,
                'numround': numRound,
                'all_problem': problem_data
            }))

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def game_hard_problem(self, event):
        try:
            numRound = event['numRound']
            room_id = event['room_id']
            timeduration = event['timeduration']
            problem_data = self.generate_hard_problem(numRound)
            self.send(text_data=json.dumps({
                'type': 'game_problem',
                'room_id': room_id,
                'timeduration': timeduration,
                'numround': numRound,
                'all_problem': problem_data
            }))

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def hard_problem(self, event):
        try:
            if 'curr_round' in event:
                curr_round = event['curr_round']
                room_id = event['room_id']

                while True:
                    target = random.randint(1000, 1500)
                    numbers = [OneFromTheTop()] + [OneOfTheOthers()
                                                   for i in range(5)]
                    solution = Solve(target, numbers)
                    if solution is not None:
                        break

                print(str(solution))
                hint = self.extract_hint(str(solution))

                self.send(text_data=json.dumps({
                    'type': 'hard_problem',
                    'room_id': room_id,
                    'curr_round': curr_round,
                    'target': target,
                    'problem': numbers,
                    'solution': solution,
                    'hint': hint
                }))
            else:
                raise ValueError("'curr_round' not found in event")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def evaluate_winner_round(self, ans1, ans2, prob, time1, time2):
        ans1 = int(ans1)
        ans2 = int(ans2)
        prob = int(prob)

        if ans1 == prob and ans2 == prob:
            if time1 < time2:
                return 'player1'
            elif time1 > time2:
                return 'player2'
            else:
                return 'tied'
        elif ans1 == prob:
            return 'player1'
        elif ans2 == prob:
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
                time1 = player_answer['player1']['time']
                time2 = player_answer['player2']['time']
                numround = event['numround']
                timeduration = event['timeduration']

                if player_answer['player1']['answer'] != "" and player_answer['player2']['answer'] != "" and player_answer['player1']["time"] != 100 and player_answer['player2']['time'] != 100:
                    winner = self.evaluate_winner_round(
                        player_answer['player1']['answer'], player_answer['player2']['answer'], problem, time1, time2)

                    if winner == 'tied':
                        self.send(text_data=json.dumps({
                            'type': 'game_answer',
                            'room_id': room_id,
                            'curr_round': curr_round,
                            'numround': numround,
                            'timeduration': timeduration,
                            'problem': problem,
                            'winner': 'tied',
                            'player_answer': 'tied'
                        }))
                    else:
                        self.send(text_data=json.dumps({
                            'type': 'game_answer',
                            'room_id': room_id,
                            'curr_round': curr_round,
                            'numround': numround,
                            'timeduration': timeduration,
                            'problem': problem,
                            'winner': player_answer[winner]['username'],
                            'player_answer': player_answer[winner]['answer'],
                            'turn': True
                        }))
                else:
                    self.send(text_data=json.dumps({
                        'type': 'game_answer',
                        'room_id': room_id,
                        'curr_round': curr_round,
                        'numround': numround,
                        'timeduration': timeduration,
                        'problem': problem,
                        'player_answer': player_answer
                    }))
                raise ValueError("Need to submit one more answer")
            else:
                raise ValueError("'player_answer' not found in event")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def game_reset(self, event):

        self.send(text_data=json.dumps({
            'type': 'game_reset',
            'reset': True,
            'message': f'The game {self.room_id} has been reset.'
        }))
