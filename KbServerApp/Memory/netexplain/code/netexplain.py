import curses

# Assuming the functions from network_info.py are imported or available
from netinfo import generate_network_info as generate_network_info


def explain_line(line):
    # This function should return an explanation for the given line
    # For this example, I'm just returning the line itself
    return "Explanation for: " + line


def display_network_info(stdscr):
    # Get the network info
    output_lines = generate_network_info()

    # Initialize curses
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(0)
    stdscr.timeout(100)

    index = 0
    while True:
        stdscr.clear()

        # Display the network info, highlighting the selected line
        for i, line in enumerate(output_lines):
            if i == index:
                stdscr.addstr(i, 0, line, curses.A_REVERSE)
            else:
                stdscr.addstr(i, 0, line)

        # Get the user's input
        key = stdscr.getch()

        # Navigate up and down the list
        if key == curses.KEY_UP and index > 0:
            index -= 1
        elif key == curses.KEY_DOWN and index < len(output_lines) - 1:
            index += 1
        elif key == ord('\n'):
            # When Enter is pressed, display the explanation
            explanation = explain_line(output_lines[index])
            stdscr.clear()
            stdscr.addstr(0, 0, explanation)
            stdscr.getch()  # Wait for another key press to continue

        # Refresh the screen
        stdscr.refresh()


curses.wrapper(display_network_info)
