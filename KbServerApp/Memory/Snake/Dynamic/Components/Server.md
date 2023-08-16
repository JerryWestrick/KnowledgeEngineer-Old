# Server

The server is responsible for managing the game logic and facilitating communication between the clients. It performs the following tasks:

- Manages the game board, which is a 100 x 100 grid of squares.
- Calculates the movement of each snake on each step of the game.
- Determines if any snakes have died.
- Tracks the squares that need color changes.
- Sends the updated game state to each client.

## Requirements

To implement the server, the following requirements should be considered:

- The server should be able to handle multiple concurrent connections from clients.
- It should have a high-performance network stack to handle the real-time nature of the game.
- The server should be able to process game logic and update the game state at a rate of 15 steps per second.
- It should have a data structure to represent the game board and track the state of each square.
- The server should be able to handle client input and update the game state accordingly.
- It should have a mechanism to detect when a snake dies and remove it from the game.
- The server should be able to send the updated game state to each client efficiently.
- It should handle the start and end of the game, including managing the countdown and announcing the winner.