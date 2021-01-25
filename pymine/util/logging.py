from prompt_toolkit import print_formatted_text as print, ANSI
from prompt_toolkit import PromptSession
import traceback
import time
import os

if os.name == "nt":
    import colorama

    colorama.init()

nice_time = lambda: time.strftime("%x %H:%M:%S")

BRIGHT = "\x1b[1m"
END = "\x1b[0m"
WHITE = "\x1b[97m"
GREY = "\x1b[37m"
BLUE = "\x1b[34m"
YELLOW = "\x1b[33m"
RED = "\x1b[91m"
BG_RED = "\x1b[41;1m"


class Logger:
    """Custom logging implementation.

    :param bool debug: Whether to show debug messages or not.
    :attr type debug_: The value of the debug parameter.
    """

    def __init__(self, prompt_ses: PromptSession, debug: bool = True) -> None:
        self._prompt_ses = prompt_ses
        self._debug = debug

    def debug(self, *message):
        if self._debug:
            message = " ".join([str(m) for m in message])
            print(ANSI(f"{WHITE}[{nice_time()} {GREY}DEBUG{WHITE}]: {GREY}{message}{END}"))

    def info(self, *message):
        message = " ".join([str(m) for m in message])
        print(ANSI(f"{BRIGHT}{WHITE}[{nice_time()} {BLUE}INFO{WHITE}]: {message}{END}"))

    def warn(self, *message):
        message = " ".join([str(m) for m in message])
        print(ANSI(f"{BRIGHT}{WHITE}[{nice_time()} {YELLOW}WARNING{WHITE}]: {YELLOW}{message}{END}"))

    warning = warn

    def error(self, *message):
        message = " ".join([str(m) for m in message])
        print(ANSI(f"{BRIGHT}{WHITE}[{nice_time()} {RED}ERROR{WHITE}]: {RED}{message}{END}"))

    def critical(self, *message):
        message = " ".join([str(m) for m in message])
        print(ANSI(f"{BRIGHT}{WHITE}{BG_RED}[{nice_time()} CRITICAL]: {message}{END}"))

    @staticmethod
    def f_traceback(e: BaseException):
        return "\n" + "".join(traceback.format_exception(type(e), e, e.__traceback__, 4)).rstrip("\n")


def task_exception_handler(loop, ctx):
    if ctx["exception"]:
        print(f'{BRIGHT}{WHITE}[{nice_time()} {RED}ERROR{WHITE}]: {RED}{Logger.f_traceback(ctx["exception"])}{END}')
    else:
        print(f'{BRIGHT}{WHITE}[{nice_time()} {RED}ERROR{WHITE}]: {RED}{ctx["message"]}{END}')


if __name__ == "__main__":  # Used to test colors
    logger = Logger()

    logger.debug("This is a", "debug message")
    logger.info("This is an", "info message")
    logger.warn("This is a", "warning message")
    logger.error("This is an", "error message")
    logger.critical("This is a", "critical error message")
