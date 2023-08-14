# Protocol

The protocol is responsible for defining the communication between the server and the clients.

## Requirements:

- The protocol must support multiple clients.
- The protocol must allow the server to send game state updates to the clients.
- The protocol must allow the clients to send arrow key state changes to the server.
- The protocol must allow the server to announce to the clients if they have died.
- The protocol must allow the server to announce the color of the last surviving snake at the end of the game.
- The protocol must support the transition between game states.