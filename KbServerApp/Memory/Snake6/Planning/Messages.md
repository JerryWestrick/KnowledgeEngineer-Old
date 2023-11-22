# Messages in Snake Online Game

## 1. Joining
- **Sender**: Client
- **Receiver**: Server
- **Description**: Sent by the client when attempting to join the game, containing the username.
- **Example**: `{"type": "Joining", "username": "Player1"}`

## 2. DirectionChange
- **Sender**: Client
- **Receiver**: Server
- **Description**: Sent by the client to change the direction of their snake.
- **Example**: `{"type": "DirectionChange", "direction": "Up"}`

## 3. SnakeDied
- **Sender**: Server
- **Receiver**: Client
- **Description**: Sent by the server to the client when their snake dies.
- **Example**: `{"type": "SnakeDied", "username": "Player1"}`

## 4. GameStatus
- **Sender**: Server
- **Receiver**: Client
- **Description**: Broadcast by the server to all clients after each tick, containing the entire game state.
- **Example**: 
  ```
  {
    "type": "GameStatus",
    "game_board": "updated game board string",
    "foods": [(x1, y1), (x2, y2)],
    "clients": {
      "websocket1": {"name": "Player1", "char": "🔴", "snake": [(5, 3), (5, 4)], "score": 130, "direction": "Up"},
      "websocket2": {"name": "Player2", "char": "🔵", "snake": [(6, 12), (6, 13)], "score": 30, "direction": "Left"}
    }
  }
  ```

## 5. WebSocket Disconnect
- **Sender**: Client
- **Receiver**: Server
- **Description**: Automatically sent by the client's browser when the WebSocket connection is closed.
- **Example**: *No explicit message, as this is a WebSocket event.*

## 6. Reset_A_Client
- **Sender**: Server (internally handled)
- **Receiver**: Server (internally handled)
- **Description**: An internal server message to reset a client's snake and score when the snake dies.
- **Example**: *No explicit message, as this is an internal server action.*

## 7. HTTP Server Startup
- **Sender**: Server (internally handled)
- **Receiver**: Server (internally handled)
- **Description**: An internal server message indicating that the HTTP server has started and is ready to serve SnakeClient.html.
- **Example**: *No explicit message, as this is an internal server action.*

Note: The messages "Reset_A_Client" and "HTTP Server Startup" are internal server actions and do not have explicit message formats exchanged between the client and server.
