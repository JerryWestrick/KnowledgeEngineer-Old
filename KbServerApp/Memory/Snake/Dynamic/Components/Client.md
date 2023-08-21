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