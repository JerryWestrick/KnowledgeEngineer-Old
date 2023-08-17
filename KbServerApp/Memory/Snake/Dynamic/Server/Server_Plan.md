Plan to implement SnakeServer.py:

1. Import necessary libraries:
    - asyncio for asynchronous I/O, networking, and concurrency.
    - websockets for WebSocket protocol handling.
    - json for encoding and decoding JSON data.

2. Define the game state:
    - A 100x100 grid to represent the game board.
    - A list of snakes, each with a position, direction, and color.
    - A list of squares that have changed since the last update.

3. Define the WebSocket server:
    - The server should listen on localhost:8090.
    - It should accept connections from multiple clients.
    - It should handle incoming messages from clients and send outgoing messages to clients.

4. Define the game loop:
    - The game should run at 15 steps per second.
    - Each step should calculate the movement of each snake, determine if any snakes die, and identify squares that need color changes.
    - After each step, the server should send a GameUpdate message to each client with the list of squares that have changed and their new colors.

5. Define the message handlers:
    - GameUpdate: The server should send this message to each client after each step of the game. The message should include a list of squares that have changed and their new colors.
    - UserInput: The server should receive this message from each client. The message should include the state of the arrow keys for the client's snake. The server should update the direction of the client's snake based on this input.
    - GameStatus: The server should send this message to a client when the client's snake dies or when the game ends. The message should include the status of the client's snake and the color of the last surviving snake.
    - Countdown: The server should send this message to each client when the first client joins after the end of a game. The message should initiate a 30-second countdown to the start of the game.

6. Define the client handlers:
    - When a client connects, the server should assign a color to the client's snake and draw the snake on the game board.
    - When a client disconnects, the server should remove the client's snake from the game.

7. Define the game start and end conditions:
    - The game should start when the first client joins after the end of a game and the 30-second countdown finishes.
    - The game should end when there is only one snake left on the game board. The server should announce the color of the last surviving snake as the winner.