# Server

The server is responsible for managing the game state and communicating with the clients. It performs the following tasks:

- Manages the game board of 100 x 100 squares.
- Calculates the game at a rate of 15 steps per second.
- Each step involves:
    - Calculating the movement of each snake.
    - Determining if any snakes die.
    - Identifying squares that need color changes.
- Sends a list of squares that changed and their new colors to each client.
- Assigns a color to each client that joins the game and draws their snake.
- Updates the state of the game based on the arrow key events received from each client.
- Announces to the client if it has died.
- Announces the color of the last surviving snake as the winner at the end of the game.
- Initiates a 30-second countdown to the start of the game when the first client joins after the end of a game.