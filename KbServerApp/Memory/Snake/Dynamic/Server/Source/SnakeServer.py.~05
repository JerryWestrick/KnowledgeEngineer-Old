import asyncio
import websockets
import json
from game_state import GameState
from snake import Snake

# Define the WebSocket server
class SnakeServer:
    def __init__(self):
        self.game_state = GameState()
        self.clients = {}

    async def handler(self, websocket, path):
        # Assign a color to the client and add a snake to the game state
        color = self.assign_color()
        snake = Snake(color)
        self.game_state.add_snake(snake)
        self.clients[websocket] = snake

        try:
            # Process messages from the client
            async for message in websocket:
                data = json.loads(message)
                if data['type'] == 'KeyEvent':
                    self.process_key_event(data['payload']['key'], snake)
        except websockets.ConnectionClosed:
            # Remove the snake from the game state when the client disconnects
            self.game_state.remove_snake(snake)
            del self.clients[websocket]

    def assign_color(self):
        # Assign a unique color to each client
        return '#' + ''.join([hex(x)[2:].zfill(2) for x in (len(self.clients), 0, 0)])

    def process_key_event(self, key, snake):
        # Update the game state based on the key event
        if key == 'ArrowUp':
            snake.move_up()
        elif key == 'ArrowDown':
            snake.move_down()
        elif key == 'ArrowLeft':
            snake.move_left()
        elif key == 'ArrowRight':
            snake.move_right()

        self.game_state.update_square(snake.get_head()[0], snake.get_head()[1], snake.color)

# Start the WebSocket server
start_server = websockets.serve(SnakeServer().handler, 'localhost', 8090)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()