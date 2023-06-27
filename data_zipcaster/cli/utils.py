import datetime
import os
import sys
import traceback
from typing import Callable, ParamSpec, TypeVar

import rich
import rich_click as click

from data_zipcaster import __version__

T = TypeVar("T")
P = ParamSpec("P")


def handle_exception(
    func: Callable[P, T]
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, click.ClickException):
                raise e

            filepath = os.path.join(os.getcwd(), "error.txt")

            with open(filepath, "a") as f:
                f.write(f"====================\n")
                f.write(f"Fatal Error Occured!\n")
                f.write(f"Date: {datetime.datetime.now()}\n")
                f.write(f"Exception: {e}\n")
                f.write(f"Version: {__version__}\n")
                f.write("".join(traceback.format_exception(*sys.exc_info())))
                f.write(f"====================\n")

            rich.print(f"Saved [bold red]ERROR[/] to [bold green]{filepath}[/]")

            raise click.ClickException(
                "A fatal error occurred. Please report this issue on "
                + "GitHub, found below this message. Your error has been "
                + "saved to the file mentioned above. Please attach this "
                + "file to your issue."
            )

    return wrapper
