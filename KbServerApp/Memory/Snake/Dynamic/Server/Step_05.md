# Step 5: Define the message handling

- When a GameUpdate message is received, update the list of changed squares and their colors in the game state.
- When a KeyEvent message is received, update the direction of the corresponding snake.
- When a DeathNotification message is received, remove the corresponding snake from the game state.
- When a WinnerAnnouncement message is received, reset the game state.
- When a GameReset message is received, reset the game state.