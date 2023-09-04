# Server Requirements

1. **SR1**: The server should be implemented in Python 3, with Async IO, aiohttp serving SnakeClient.html, and connect via websockets.
2. **SR2**: The server should maintain a game board, a 100 x 100 2D character representation of the playing ground.
3. **SR3**: The server should keep the game board up to date with the values of Snakes and Foods.
4. **SR4**: The server should implement the game as Ticks, with 5 ticks per second.
5. **SR5**: The server should move each snake whose direction is not 'Stop' during each tick.
6. **SR6**: The server should check for collisions by checking the value of the character in the game board at position (x, y).
7. **SR7**: The server should handle snake death and client reset scenarios.
8. **SR8**: The server should send GameStatus to all connected clients after each tick.
9. **SR9**: The server should handle "Joining" messages from clients.
10. **SR10**: The server should handle websocket disconnections.
11. **SR11**: The server should start a HTTP Server that serves the file SnakeClient.html at startup.