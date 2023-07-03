import datetime
import os

import colors
from textwrap import wrap, fill


class Logger:
    """
    A logger class that prints log messages to the console if logging is enabled for a specific action,
    and always appends log messages to a log file.

    The Logger is initialized with a log file path via Logger(log_file).

    The Logger class is a singleton, and is used via the static methods:
        Logger.enable_logging
        Logger.disable_logging
        Logger.log

    Usage:
        logger = Logger('log.txt')
        logger.enable_logging('action1')
        logger.log('action1', 'This is a log message for action1')

    Args:
        log_file (str): The path to the log file.

    Attributes:
        log_file (str): The path to the log file.
        logging_actions (dict): A dictionary to store the enabled logging actions.

    """

    logging_actions = {
        'SYSTEM': True,
        'LLM': True,
        'PROMPT': True,
        'REPLY': True,
        'EXEC': True,
        'ERROR': True,
        'INFO': True,
        'DEBUG': True,
        'WARNING': True,
        'RUN': True,
        'STEP': True,
        'MEMORY': True,
        'RESPONSE': True,
    }
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, log_file: str):
        """
        Initializes a Logger instance with the specified log file.

        Args:
            log_file (str): The path to the log file.

        """

        if not hasattr(self, 'log_file'):
            self.log_file = log_file
            self.__logging_colors = {
                'SYSTEM': colors.SYSTEM,
                'LLM': colors.LLM,
                'PROMPT': colors.PROMPT,
                'REPLY': colors.REPLY,
                'EXEC': colors.EXEC,
                'ERROR': colors.ERROR,
                'INFO': colors.INFO,
                'DEBUG': colors.DEBUG,
                'WARNING': colors.WARNING,
                'RUN': colors.RUN,
                'STEP': colors.STEP,
                'MEMORY': colors.MEMORY,
                'RESPONSE': colors.RESPONSE,
            }

            if os.path.exists(log_file):
                os.remove(log_file)

            directory = os.path.dirname(log_file)  # Get the directory path
            os.makedirs(directory, exist_ok=True)  # Create the directory if it doesn't exist

            with open(log_file, 'w') as file:
                action = "Create"

                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"[{current_time}] {action}: Creation of Log File {log_file}"
                file.write(log_entry + '\n')
                print(f'{colors.DEFAULT}{log_entry}')

    def __set_color(self, action: str, color: str):
        """
        Sets the color for a log element for a specific action.

        Args:
            action (str): The action to set the color for.
            color (str): The color to set.

        """
        self.__logging_colors[action] = color

        def __enable_logging(self, action):
            """
            Enables logging for a specific action.

            Args:
                action (str): The action to enable logging for.

            """

        self.logging_actions[action] = True

    def __disable_logging(self, action):
        """
        Disables logging for a specific action.

        Args:
            action (str): The action to disable logging for.

        """

        self.logging_actions[action] = False

    def __log(self, action=None, message=None):
        """
        Logs a message for a specific action. The message is printed to the console if logging is enabled for that action,
        and it is appended to the log file.

        Args:
            action (str, optional): The action to log the message for. Defaults to 'default'.
            message (str, optional): The log message to be logged. Defaults to None.

        """

        if action is None:
            action = "default"

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{current_time}] {action}: {message}"

        # With wrapped strings...
        # current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # max_width = 255
        # first = f"[{current_time}] {action}: "
        # rest = '\n' + ' ' * len(first)
        # left_margin = first
        # log_entry = ''
        # lines = message.splitlines()
        # for line in lines:
        #     wrapped_string = ''
        #     partials = wrap(line, max_width)
        #     for partial in partials:
        #         wrapped_string = left_margin + partial
        #         left_margin = rest
        #     log_entry += wrapped_string

        if action not in self.logging_actions:
            self.logging_actions[action] = True

        if self.logging_actions[action]:
            color = self.__logging_colors.get(action, colors.DEFAULT)
            print(f'{color}{log_entry}')

        with open(self.log_file, 'a') as file:
            file.write(log_entry + '\n')

    @staticmethod
    def log(action: str, message: str):
        """
        Static method to log a message without creating an instance of the Logger class.

        Args:
            action (str, optional): The action to log the message for. Defaults to 'default'.
            message (str, optional): The log message to be logged. Defaults to None.

        """

        logger = Logger.get_instance()
        logger.__log(action, message)

    @staticmethod
    def enable_logging(action):
        """
        Static method to enable logging for a specific action without creating an instance of the Logger class.

        Args:
            action (str): The action to enable logging for.

        """

        logger = Logger.get_instance()
        logger.__enable_logging(action)

    @staticmethod
    def disable_logging(action):
        """
        Static method to disable logging for a specific action without creating an instance of the Logger class.

        Args:
            action (str): The action to disable logging for.

        """

        logger = Logger.get_instance()
        logger.__disable_logging(action)

    @classmethod
    def get_instance(cls):
        """
        Returns the global instance of the Logger class.

        Returns:
            Logger: The global instance of the Logger class.

        """

        if not cls._instance:
            cls._instance = Logger('log.txt')
        return cls._instance
