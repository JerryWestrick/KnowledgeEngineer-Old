# Step 6: Define the message sending

- At each step, send a GameUpdate message to all clients with the list of changed squares and their new colors.
- When a snake dies, send a DeathNotification message to its client.
- When the game ends, send a WinnerAnnouncement message to all clients with the color of the last surviving snake.
- After the game ends, send a GameReset message to all clients.