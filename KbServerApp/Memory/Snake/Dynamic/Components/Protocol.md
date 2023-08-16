# Protocol

The protocol defines the communication between the server and the clients. It includes the following messages:

- JoinGame: Sent by the client to join the game.
- StartGame: Sent by the server to indicate the start of the game.
- UpdateGameState: Sent by the server to update the game state.
- PlayerDeath: Sent by the server to notify the client of the player's snake death.
- Winner: Sent by the server to announce the winner of the game.
- RestartGame: Sent by the server to indicate the start of a new game.

The protocol should be designed to be efficient and minimize network traffic. It should also handle any potential errors or disconnections gracefully.