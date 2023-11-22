
# Game constants
    BOARD_SIZE = 100
    SNAKE_CHARACTERS = ["🔴", "🔵", "🟠", "🟡", "🟢", "🟣", "🟤"]
    FOOD_CHAR = "🍎"
    FOOD_COUNT = 5
    DIRECTION = {"Stop": (0, 0), "Up": (0,-1), "Down": (0,1), "Left": (-1,0), "Right": (1,0) }
    
    
    GameStatus = {
        "game_board": " " * (BOARD_SIZE * BOARD_SIZE),  # (100 strings of 100 spaces)
        "free_snake_chars": ["🔴", "🔵", "🟠", "🟡", "🟢", "🟣", "🟤"],
        "foods": [(50, 2), (5, 20), (34, 12), (50, 2), (12, 98)],
        "clients": {
          websocket1: {"name": "Jerry", "char": "🔴", "snake": [(5, 3), (5, 4), (6, 4)], "score": 127, "direction": "Up"},
          websocket2: {"name": "Tom", "char": "🔵", "snake": [(6, 12), (6, 13), (6, 14)], "score": 27, "direction": "Left"}
        }
    }

### Note: 

GameStatus['clients'] should be {} (empty), 
because websocket1, websocket2 will be added at runtime 


# The Server side of a multi-user "Snake" online game.

## Server is SnakeServer.py

#### Architecture: 
python 3, with Async IO, aiohttp serving SnakeClient.html, and connect via websockets

#### The game_board 
(a 100 x 100 2d character representation of the playing ground) is kept up to date with the values of Snakes and Foods; Therefor you can check for collisions by checking the value of the character in the game_board at position (x, y).

#### Ticks Logic:
The game is implemented as Ticks (5 per second).
##### Tick:
    1. move each snake who's direction is not 'Stop':
        new_head = head of snake + snake direction.

        if new_head x or y are not in bounds: Snake_Dies
        if game_board at new_head is a snake character: Snake_Dies.

        if game_board at new_head is a food:
            - game_board at new_head draw client char
            - push new_head (x, y) onto front of snake
            - remove new_head from foods.
            - find a random (fx, fy) that is Space, add it to foods, and draw food char.
            - add 100 to snake score.

        if game_board at new_head is Space:
            - game_board at new_head draw client char
            - push new_head (x, y) onto front of snake
            - pop last position from snake as tail.
            - game_board at tail draw space
            - add 1 to snake score

    2. Send GameStatus to all connected Clients.

##### Snake_Dies:
    - Send SnakeDied message to client.
    - erase client snake from the board.
    - Do Reset_A_Client:

##### Reset_A_Client:
    - new snake head is at random position so new snake is [(x, y), (x, y+1), (x, y+2)]
        where game_board at each [(x, y), (x, y+1), (x, y+2)] == space
            set client snake to new snake
    - draw Client snake on game_board
    - the Client score is set to zero
    - the Client direction is set to "Stop"

##### When Server receives "Joining":
    - if free_snake_chars is empty then close websocket
    - take a char from free_snake_chars and assign it to the Client as 'char'.
    - the client['username']= username
    - Do Reset_A_Client.

##### Server When websocket disconnect:
    - return Client char to game_state free_snake_chars.
    - erase client snake from game_board
    - del game_status['clients'][websocket]

##### Server At Startup:
    - At startup The Server will start a HTTP Server that serves the file SnakeClient.html

# implement the client of a multi-user "Snake" online game.
## The Client part is SnakeClient.html
The Client part is a single file containing html, css, and javascript called SnakeClient.html

#### Client Architecture: 
use html, css, javascript, websockets all in a single file.

#### Display Artifacts:
##### GameBoard:
- The GameBoard is a 2d 100 x 100 character array with default character " ".
- The Board needs a frame.
- The Board needs to be resizable, the characters displayed in board need to be resized with board.

##### Client List:
- The client list is displayed in a status bar at bottom of window.
- display "{client.char}{client.username}:{client.score} " for each client in game_status.clients
- for example: "🔴Jerry:150  🔵Tom:423"

##### Client initialization:
- the Client prompts the user for a username.
- the Client connects via websocket
- the Client sends a "Joining" message (which includes the username).

##### Client detects arrow keys:
- it sends "DirectionChange" message with 'Up', 'Down', 'Left', or 'Right', which starts the client.

##### Client receives SnakeDied:
- client shows pop-up dialog.

##### Client receives GameStatus:
- replace GameBoard and Client List with values from message


