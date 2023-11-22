# Client Requirements for Snake Online Game

## 1. Single HTML File
- The client must be contained within a single HTML file, named SnakeClient.html.
- This file should include HTML, CSS, and JavaScript necessary for the client's functionality.

## 2. WebSockets Communication
- The client must use WebSockets to communicate with the server in real-time.
- It should handle messages such as "Joining", "DirectionChange", "SnakeDied", and "GameStatus".

## 3. User Interface
- The client must prompt the user for a username upon initialization.
- It should display the game board and a status bar with the client list.

## 4. Game Board Display
- The game board must be a 2D 100x100 character array with a default character " ".
- It should be displayed with a frame and be resizable, with characters resizing accordingly.

## 5. Client List in Status Bar
- The status bar must display the score and character for each client in the format "{client.char}{client.username}:{client.score}".
- It should update in real-time as the game status changes.

## 6. Handling User Input
- The client must detect arrow key presses and send direction change messages to the server.
- It should start the snake's movement based on the user's input.

## 7. Displaying Game Updates
- The client must update the game board and client list based on the "GameStatus" messages from the server.
- It should ensure that the display is consistent with the current state of the game.

## 8. Handling Game Events
- The client must show a pop-up dialog when the "SnakeDied" message is received.
- It should handle other game events as defined by the server's communication protocol.

## 9. Error Handling and Reconnection
- The client should handle network errors gracefully and attempt to reconnect if the connection is lost.
- It must inform the user of any issues that prevent normal gameplay.

## 10. Visual and Aesthetic Design
- The client's interface must be visually appealing and user-friendly.
- It should provide a clear and intuitive gaming experience.

## 11. Cross-Browser Compatibility
- The client must be compatible with major web browsers, including Chrome, Firefox, and Safari.
- It should ensure consistent behavior and appearance across these platforms.

## 12. Responsive Design
- The client's interface must be responsive and adapt to different screen sizes and resolutions.
- It should provide an optimal viewing experience on both desktop and mobile devices.

## 13. Security Considerations
- The client must handle data received from the server securely.
- It should validate and sanitize input to prevent security vulnerabilities such as XSS attacks.

## 14. Performance Optimization
- The client must be optimized for performance to handle rapid updates and rendering.
- It should minimize latency and ensure smooth gameplay.

## 15. Accessibility
- The client should be accessible to users with disabilities.
- It must comply with accessibility standards to ensure that all players can enjoy the game.
