# Client

The client is responsible for interacting with the user and communicating with the server. It performs the following tasks:

- Displays a "Join the game" pop-up with a countdown to game start when connected.
- Provides Yes/No buttons for the user to join or decline to join the game.
- Closes the pop-up when the user joins the game, declines to join, or when the game starts.
- Displays the entire game board to the user once they join the game.
- Displays a countdown to game start.
- Sends any change event to the state of the arrow keys to the server.
- Updates its view of the game board based on the update commands received from the server.
- Continues to update the screen after the user's snake has died until the end of the game.
- Displays a "Winner" message stating the color of the last surviving snake at the end of the game until "ok" is clicked.
- Displays the "Join the Game" pop-up after the end of the game, but does not initiate a countdown until the first client joins.