SnakeServer.py
```python
import asyncio
import websockets
import http.server
import json
import os
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

class Game:
    def __init__(self):
        self.board = [[0 for _ in range(100)] for _ in range(100)]
        self.snakes = []
        self.dead_snakes = []

    def initialize_game(self):
        # Initialize game state here

    def update_game_state(self):
        # Update game state here

    def detect_death(self):
        # Detect snake deaths here

    def announce_winner(self):
        # Announce winner here

    def handle_client_input(self, input):
        # Handle client input here

class SnakeServer(websockets.WebSocketServerProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clients = set()
        self.game = Game()

    async def connection_made(self, ws):
        self.clients.add(ws)

    async def connection_lost(self, ws):
        self.clients.remove(ws)

    async def receive_message(self, ws, message):
        # Parse the incoming JSON message
        data = json.loads(message)

        # Handle the message based on its type
        if data['type'] == 'JoinGame':
            self.handle_join_game(ws, data)
        elif data['type'] == 'StartGame':
            self.handle_start_game(ws, data)
        elif data['type'] == 'UpdateGameState':
            self.handle_update_game_state(ws, data)
        elif data['type'] == 'PlayerDeath':
            self.handle_player_death(ws, data)
        elif data['type'] == 'Winner':
            self.handle_winner(ws, data)
        elif data['type'] == 'RestartGame':
            self.handle_restart_game(ws, data)

    def handle_join_game(self, ws, data):
        # Handle JoinGame message here

    def handle_start_game(self, ws, data):
        # Handle StartGame message here

    def handle_update_game_state(self, ws, data):
        # Handle UpdateGameState message here

    def handle_player_death(self, ws, data):
        # Handle PlayerDeath message here

    def handle_winner(self, ws, data):
        # Handle Winner message here

    def handle_restart_game(self, ws, data):
        # Handle RestartGame message here

class SnakeHTTPServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":
    web_dir = os.path.join(os.path.dirname(__file__), 'web')
    os.chdir(web_dir)

    httpd = TCPServer(("", 8090), SnakeHTTPServer)
    print("serving at port", 8090)
    httpd.serve_forever()

    start_server = websockets.serve(SnakeServer, 'localhost', 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
```