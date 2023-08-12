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