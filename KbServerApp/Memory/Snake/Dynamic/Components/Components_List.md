Server.md
```markdown
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
```

Client.md
```markdown
# Client

The client is responsible for interacting with the user and communicating with the server.

## Requirements:

- The client must display a "Join the game" pop-up with a countdown to game start.
- The client must provide Yes/No buttons for the user to join or decline the game.
- The client must close the pop-up when the user joins the game, declines the game, or when the game starts.
- The client must display the entire game board.
- The client must display a countdown to game start.
- The client must update the server of any change event to the state of the arrow keys.
- The client must update its view of the game board with the update commands received from the server.
- The client must display a "Winner" message stating the color of the last surviving snake at the end of the game.
- The client must display the winner until "ok" is clicked.
- The client must display the "Join the Game" pop-up after the end of the game.
```

Protocol.md
```markdown
# Protocol

The protocol is responsible for defining the communication between the server and the clients.

## Requirements:

- The protocol must support multiple clients.
- The protocol must allow the server to send game state updates to the clients.
- The protocol must allow the clients to send arrow key state changes to the server.
- The protocol must allow the server to announce to the clients if they have died.
- The protocol must allow the server to announce the color of the last surviving snake at the end of the game.
- The protocol must support the transition between game states.
```