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
- Announces the color of the last surviving snake as the winner at the end of the game.
- Initiates a 30-second countdown to the start of the game when the first client joins after the end of a game.
```

Client.md
```markdown
# Client

The client is responsible for interacting with the user and communicating with the server. It performs the following tasks:

- Displays a "Join the game" pop-up with a countdown to game start when connected.
- Provides Yes/No buttons for the user to join or decline to join the game.
- Closes the pop-up when the user joins the game, declines to join, or when the game starts.
- Displays the entire game board to the user.
- Displays a countdown to game start once the user has joined the game.
- Sends any change event to the state of the arrow keys to the server.
- Updates its view of the game board with the update commands received from the server.
- Continues to update the screen until the end of the game, even if the client has died.
- Displays a "Winner" message stating the color of the last surviving snake at the end of the game until "ok" is clicked.
- Displays the "Join the Game" pop-up after the end of the game, but does not initiate a countdown until the first client joins.
```

Protocol.md
```markdown
# Protocol

The protocol is responsible for defining the communication between the server and the clients. It should support the following operations:

- Server to client:
    - Send the color assigned to the client and draw their snake.
    - Send a list of squares that changed and their new color.
    - Announce to the client if it has died.
    - Announce the color of the last surviving snake as the winner at the end of the game.
    - Initiate a 30-second countdown to the start of the game when the first client joins after the end of a game.

- Client to server:
    - Send a join or decline to join the game command.
    - Send any change event to the state of the arrow keys.
```