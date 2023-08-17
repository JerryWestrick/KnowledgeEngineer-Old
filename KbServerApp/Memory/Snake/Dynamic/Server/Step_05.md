# Step 5: Define the message handlers

- GameUpdate: The server should send this message to each client after each step of the game. The message should include a list of squares that have changed and their new colors.
- UserInput: The server should receive this message from each client. The message should include the state of the arrow keys for the client's snake. The server should update the direction of the client's snake based on this input.
- GameStatus: The server should send this message to a client when the client's snake dies or when the game ends. The message should include the status of the client's snake and the color of the last surviving snake.
- Countdown: The server should send this message to each client when the first client joins after the end of a game. The message should initiate a 30-second countdown to the start of the game.