# Server

The server is responsible for managing the game state and communicating with the clients. It performs the following tasks:

- Manages the game board of 100 x 100 squares.
- Calculates the game at a rate of 15 steps per second.
- Each step, the server calculates:
    - The movement of each snake.
    - Determines if any snakes die.
    - Determines what squares need color changes.
- Sends a list of squares that changed and their new color to each client.
- Assigns a color to each client that joins the game and draws their snake.
- Updates the state of the game based on the arrow key events received from each client.
- Announces to the client if it has died.
- Announces the winner of the game when only one snake remains.
- Resets the game after it ends and waits for the first client to join to start a new game.