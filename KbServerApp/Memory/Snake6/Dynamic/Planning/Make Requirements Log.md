filename=Messages.md
```markdown
# Messages

1. **Joining**
    - **Sender**: Client
    - **Receiver**: Server
    - **Description**: Sent when a client is joining the game. It includes the username of the client.
    - **Example**: `{"type": "Joining", "username": "Jerry"}`

2. **DirectionChange**
    - **Sender**: Client
    - **Receiver**: Server
    - **Description**: Sent when a client changes direction using arrow keys. It includes the new direction.
    - **Example**: `{"type": "DirectionChange", "direction": "Up"}`

3. **SnakeDied**
    - **Sender**: Server
    - **Receiver**: Client
    - **Description**: Sent when a client's snake dies. It may include the reason for the snake's death.
    - **Example**: `{"type": "SnakeDied", "reason": "Collision with another snake"}`

4. **GameStatus**
    - **Sender**: Server
    - **Receiver**: Client
    - **Description**: Sent after each tick to update all clients about the current state of the game. It includes the game board, the list of foods, and the list of clients with their scores, characters, and snakes.
    - **Example**: `{"type": "GameStatus", "game_board": " " * (100 * 100), "foods": [(50, 2), (5, 20), (34, 12), (50, 2), (12, 98)], "clients": {"websocket1": {"name": "Jerry", "char": "🔴", "snake": [(5, 3), (5, 4), (6, 4)], "score": 127, "direction": "Up"}, "websocket2": {"name": "Tom", "char": "🔵", "snake": [(6, 12), (6, 13), (6, 14)], "score": 27, "direction": "Left"}}}`
```