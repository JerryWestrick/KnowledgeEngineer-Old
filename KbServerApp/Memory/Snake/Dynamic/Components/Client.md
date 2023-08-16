# Client

The client is responsible for rendering the game board and handling user input. It performs the following tasks:

- Connects to the server and joins the game.
- Displays the game board and the player's snake.
- Shows a countdown to the start of the game.
- Updates the server with any change events to the state of the arrow keys.
- Receives updates from the server and updates the game board accordingly.
- Displays a message if the player's snake dies.
- Shows the winner message at the end of the game.

## Requirements

To implement the client, the following requirements should be considered:

- The client should have a graphical user interface to display the game board and messages.
- It should be able to connect to the server and establish a network connection.
- The client should be able to send user input to the server, indicating changes to the state of the arrow keys.
- It should receive updates from the server and update the game board accordingly.
- The client should be able to render the game board and the player's snake in real-time.
- It should display a countdown to the start of the game and update it as necessary.
- The client should handle messages from the server, such as notifications of snake death and the winner message at the end of the game.