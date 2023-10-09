import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import random
import math


class gameConsumer(WebsocketConsumer):
    def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.room_group_id = 'game_%s' % self.room_id
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_id,
                self.channel_name
            )
            print(self.channel_name)
            self.accept()
        except KeyError as key_error:
            print(f"Key error: {key_error}")
            self.close()

    def disconnect(self, close_code):
        try:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_id,
                self.channel_name,
            )
        except Exception as e:
            print(f"An unexpected error occurred during disconnect: {e}")

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
            else:
                print(f"Received unsupported message type: {message_type}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    def receive_game_data(self, text_data):
        try:
            text_data_json = text_data
            if 'player_data' in text_data_json:
                player_data = text_data_json['player_data']

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_id,
                    {
                        'type': 'game_data',
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
            if 'game_round' in text_data_json:
                game_round = text_data_json['game_round']

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_id,
                    {
                        'type': 'game_problem',
                        'game_round': game_round,
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
            if 'game_round' in text_data_json:
                game_round = text_data_json['game_round']
                player_answer = text_data_json['player_answer']
                problem = text_data_json['problem']

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_id,
                    {
                        'type': 'game_answer',
                        'game_round': game_round,
                        'player_answer': player_answer,
                        'problem': problem
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

    def game_data(self, event):
        try:
            if 'player_data' in event:
                player_data = event['player_data']

                self.send(text_data=json.dumps({
                    'room_group_id': self.room_group_id,
                    'player_data': player_data,
                }))
            else:
                raise ValueError("'player_data' not found in event")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def game_problem(self, event):
        try:
            if 'game_round' in event:
                game_round = event['game_round']
                prob = []
                for num in range(5):
                    prob.append(random.randint(0, 9))
                self.send(text_data=json.dumps({
                    'room_group_id': self.room_group_id,
                    'game_round': game_round,
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
            if 'problem' in event:
                problem = event['problem']
                print(problem)
            if 'game_round' in event:
                game_round = event['game_round']
                winner = self.evaluate_winner_round(
                    player_answer['player1']['answer'], player_answer['player2']['answer'], problem)
                print(winner)
                self.send(text_data=json.dumps({
                    'room_group_id': self.room_group_id,
                    'game_round': game_round,
                    'problem': problem,
                    'winner': winner,
                    'player_answer': player_answer['player1']['answer']
                }))
            else:
                raise ValueError("'game_round' not found in event")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
