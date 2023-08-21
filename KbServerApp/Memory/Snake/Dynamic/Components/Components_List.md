Server.md
```markdown
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
```

Client.md
```markdown
# Client

The client is responsible for interacting with the user and communicating with the server. It performs the following tasks:

- Displays a "Join the game" pop-up with a countdown to game start when connected to the server.
- Allows the player to join or decline to join the game.
- Displays the entire game board and a countdown to game start once the player joins the game.
- Sends any change event to the state of the arrow keys to the server.
- Updates its view of the game board based on the update commands received from the server.
- Displays a "Winner" message stating the color of the last surviving snake when the game ends.
- Continues to update the screen after the client's snake has died until the end of the game.
- Displays the "Join the Game" pop-up after the end of the game.
```

Protocol.md
```markdown
# Protocol

The protocol is responsible for defining the communication between the server and the clients. It includes the following:

- The server sends a list of squares that changed and their new color to each client at each step.
- The client sends any change event to the state of the arrow keys to the server.
- The server sends an announcement to the client if it has died.
- The server sends a "Winner" message stating the color of the last surviving snake when the game ends.
- The server sends a reset command to the clients after the game ends to start a new game.
```