# Step 4: Define the game loop

- The game should run at 15 steps per second.
- Each step should calculate the movement of each snake, determine if any snakes die, and identify squares that need color changes.
- After each step, the server should send a GameUpdate message to each client with the list of squares that have changed and their new colors.