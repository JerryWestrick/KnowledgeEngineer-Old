# Snake_Constants.py

# Game board size
BOARD_SIZE = 100

# Characters representing snakes
SNAKE_CHARACTERS = ["🔴", "🔵", "🟠", "🟡", "🟢", "🟣", "🟤"]

# Character representing food
FOOD_CHAR = "🍎"

# Number of food items on the board
FOOD_COUNT = 5

# Directions for snake movement
DIRECTION = {
    "Stop": (0, 0),
    "Up": (0, -1),
    "Down": (0, 1),
    "Left": (-1, 0),
    "Right": (1, 0)
}

# Initial game status
GameStatus = {
    "game_board": " " * (BOARD_SIZE * BOARD_SIZE),
    "free_snake_chars": SNAKE_CHARACTERS.copy(),
    "foods": [(50, 2), (5, 20), (34, 12), (50, 2), (12, 98)],
    "clients": {}
}
