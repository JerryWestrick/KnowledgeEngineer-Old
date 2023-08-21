# Step 4: Define the game loop

- The loop should run at a rate of 15 steps per second.
- Each step, calculate the movement of each snake based on the last KeyEvent received from its client.
- If a snake moves into a wall or another snake, remove it from the game state and send a DeathNotification to its client.
- If a snake moves into a free square, add the square to the snake and to the list of changed squares.
- If only one snake remains, send a WinnerAnnouncement to all clients and reset the game state.