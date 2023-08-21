Step_01.md
```md
# Step 1: Import necessary libraries

- Import asyncio for asynchronous I/O, networking, and concurrency.
- Import websockets for WebSocket protocol handling.
- Import json for JSON message encoding and decoding.
```

Step_02.md
```md
# Step 2: Define the game state

- Define a 100x100 grid to represent the game board.
- Define a list of snakes, each represented by a list of squares and a color.
- Define a list of squares that have changed since the last step.
```

Step_03.md
```md
# Step 3: Define the WebSocket server

- The server should listen on localhost:8090.
- When a client connects, assign them a color and add a snake to the game state.
- When a client disconnects, remove their snake from the game state.
```

Step_04.md
```md
# Step 4: Define the game loop

- The loop should run at a rate of 15 steps per second.
- Each step, calculate the movement of each snake based on the last KeyEvent received from its client.
- If a snake moves into a wall or another snake, remove it from the game state and send a DeathNotification to its client.
- If a snake moves into a free square, add the square to the snake and to the list of changed squares.
- If only one snake remains, send a WinnerAnnouncement to all clients and reset the game state.
```

Step_05.md
```md
# Step 5: Define the message handling

- When a GameUpdate message is received, update the list of changed squares and their colors in the game state.
- When a KeyEvent message is received, update the direction of the corresponding snake.
- When a DeathNotification message is received, remove the corresponding snake from the game state.
- When a WinnerAnnouncement message is received, reset the game state.
- When a GameReset message is received, reset the game state.
```

Step_06.md
```md
# Step 6: Define the message sending

- At each step, send a GameUpdate message to all clients with the list of changed squares and their new colors.
- When a snake dies, send a DeathNotification message to its client.
- When the game ends, send a WinnerAnnouncement message to all clients with the color of the last surviving snake.
- After the game ends, send a GameReset message to all clients.
```

Step_07.md
```md
# Step 7: Start the WebSocket server and the game loop

- Start the WebSocket server.
- Start the game loop.
```