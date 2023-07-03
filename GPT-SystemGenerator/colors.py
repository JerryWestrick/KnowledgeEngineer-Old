import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)


DEFAULT = Style.RESET_ALL + Fore.GREEN
RUN = Style.RESET_ALL + Fore.WHITE

SYSTEM = Style.RESET_ALL + Fore.BLUE
LLM = Style.RESET_ALL + Fore.GREEN
PROMPT = Style.RESET_ALL + Fore.YELLOW
RESPONSE = Style.RESET_ALL + Fore.CYAN
REPLY = Style.RESET_ALL + Fore.MAGENTA
STEP = Style.RESET_ALL + Fore.GREEN
MEMORY = Style.RESET_ALL + Fore.CYAN


EXEC = Back.WHITE + Fore.BLACK + Style.BRIGHT
ERROR = Back.RED + Fore.WHITE + Style.BRIGHT

INFO = Back.BLUE + Fore.WHITE + Style.BRIGHT
DEBUG = Back.BLUE + Fore.CYAN + Style.BRIGHT
WARNING = Back.BLUE + Fore.YELLOW + Style.BRIGHT

