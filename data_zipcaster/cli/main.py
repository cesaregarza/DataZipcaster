import os
import time
from typing import Callable, ParamSpec, TypeVar

import cmd2
from colorama import Fore, Style, just_fix_windows_console

just_fix_windows_console()

BOLD = "\033[1m"
UNDERLINE = "\033[4m"
DATA_ZIPCASTER_TEXT = Fore.GREEN + BOLD + "Data Zipcaster" + Style.RESET_ALL

T = TypeVar("T")
P = ParamSpec("P")


class MainShell(cmd2.Cmd):
    intro = (
        "Welcome to "
        + DATA_ZIPCASTER_TEXT
        + ", a tool for exporting "
        + Fore.BLUE
        + BOLD
        + "Splatoon 3"
        + Style.RESET_ALL
        + "data to anywhere, from anywhere."
        + "\n"
        + "Please enter a command to get started or type "
        + Fore.YELLOW
        + BOLD
        + "help"
        + Style.RESET_ALL
        + " for a list of commands."
    )
    prompt = "[" + Fore.GREEN + "Zipcaster" + Style.RESET_ALL + "]> "

    def postloop(self) -> None:
        self.poutput("Thank you for using " + DATA_ZIPCASTER_TEXT + "!")

    def print_error(self, msg: str) -> None:
        self.poutput(BOLD + Fore.RED + "ERROR: " + Style.RESET_ALL + msg)
