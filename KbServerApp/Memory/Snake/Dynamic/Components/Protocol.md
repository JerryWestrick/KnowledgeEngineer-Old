# Protocol

The protocol is responsible for defining the communication between the server and the clients. It includes the following:

- The server sends a list of squares that changed and their new color to each client at each step.
- The client sends any change event to the state of the arrow keys to the server.
- The server sends an announcement to the client if it has died.
- The server sends a "Winner" message stating the color of the last surviving snake when the game ends.
- The server sends a reset command to the clients after the game ends to start a new game.