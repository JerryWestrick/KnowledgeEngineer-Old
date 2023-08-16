# Step 2: Define the WebSocket server class

- Create a class called `SnakeServer` that inherits from `websockets.WebSocketServerProtocol`.
- Implement the `__init__` method to initialize the server.
- Implement the `connection_made` method to handle new client connections.
- Implement the `connection_lost` method to handle client disconnections.
- Implement the `receive_message` method to handle incoming messages from clients.