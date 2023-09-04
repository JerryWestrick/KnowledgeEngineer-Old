# Client Requirements

1. **CR1**: The client should be implemented as a single file containing HTML, CSS, and JavaScript called SnakeClient.html.
2. **CR2**: The client should display a GameBoard, a 2D 100 x 100 character array with default character " ".
3. **CR3**: The client should display a client list in a status bar at the bottom of the window.
4. **CR4**: The client should prompt the user for a username during initialization.
5. **CR5**: The client should connect via websocket during initialization.
6. **CR6**: The client should send a "Joining" message (which includes the username) during initialization.
7. **CR7**: The client should detect arrow keys and send "DirectionChange" message with 'Up', 'Down', 'Left', or 'Right'.
8. **CR8**: The client should handle "SnakeDied" messages by showing a pop-up dialog.
9. **CR9**: The client should handle "GameStatus" messages by replacing GameBoard and Client List with values from the message.
10. **CR10**: The GameBoard needs a frame and should be resizable, the characters displayed in board need to be resized with board.