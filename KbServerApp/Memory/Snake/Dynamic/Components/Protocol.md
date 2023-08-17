# Protocol

The protocol is responsible for defining the communication between the server and the clients. It includes the following:

- The server sends a list of squares that changed and their new colors to each client.
- The client sends any change event to the state of the arrow keys to the server.
- The server sends an announcement to the client if it has died.
- The server sends an announcement of the color of the last surviving snake as the winner at the end of the game.
- The server initiates a 30-second countdown to the start of the game when the first client joins after the end of a game.