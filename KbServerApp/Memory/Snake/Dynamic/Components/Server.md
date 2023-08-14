# Server

The server is responsible for managing the game state and communicating with the clients. 

## Requirements:

- The server must be able to handle multiple clients.
- The server must calculate the game state 15 times per second. This includes:
    - The movement of each snake.
    - Determining if any snakes die.
    - Determining what squares need color changes.
- The server must send a list of squares that changed and their new color to each client.
- The server must assign a color to each client that joins the game and draw their snake.
- The server must update the state of the arrow keys for each client that joined the game.
- The server must announce to the client if it has died.
- The server must announce the color of the last surviving snake at the end of the game.
- The server must manage the game start countdown and the transition between game states.