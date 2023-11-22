# Server Requirements for Snake Online Game

## 1. Python 3 and Async IO
- The server must be implemented using Python 3.
- It should utilize asynchronous I/O operations to handle multiple clients efficiently.

## 2. aiohttp Web Server
- The server should use the aiohttp library to serve the SnakeClient.html file.
- It must be capable of handling HTTP requests and serving static files.

## 3. WebSockets Support
- The server must support WebSockets for real-time communication with clients.
- It should handle incoming connections, messages, and disconnections.

## 4. Game Board Management
- The server must maintain a 100x100 2D character array representing the game board.
- It should update the game board with snake and food positions to detect collisions.

## 5. Game Tick Logic
- The server must implement game ticks at a rate of 5 per second.
- Each tick involves moving snakes, checking for collisions, updating scores, and managing food items.

## 6. Snake Movement and Collision Detection
- The server must calculate new snake head positions based on their direction.
- It should detect collisions with the game board boundaries, other snakes, or food.

## 7. Score and Food Management
- The server must update scores when snakes eat food.
- It should generate new food items at random empty spaces on the game board.

## 8. Client Management
- The server must manage a list of connected clients and their snakes.
- It should handle client join requests, direction changes, and disconnections.

## 9. Client Character Assignment
- The server must assign a unique character to each client from a predefined set.
- It should manage the pool of available characters and reassign them as clients join or leave.

## 10. Client Reset and Snake Respawn
- The server must reset a client's snake and score when the snake dies.
- It should respawn the snake at a random position where there is space on the game board.

## 11. Message Broadcasting
- The server must broadcast the current game status to all connected clients after each tick.

## 12. Handling Client Messages
- The server must handle "Joining", "DirectionChange", and other relevant messages from clients.

## 13. HTTP Server Startup
- The server must start an HTTP server at startup to serve the SnakeClient.html file.

## 14. Resource Cleanup
- The server should perform necessary cleanup when clients disconnect or the server shuts down.

## 15. Error Handling
- The server must handle exceptions and errors gracefully to maintain continuous operation.
