import datetime
import logging
import os
import sys
import traceback
from typing import Callable, ParamSpec, TypeVar

import rich
import rich_click as click
from rich.progress import Progress

from data_zipcaster import __version__

T = TypeVar("T")
P = ParamSpec("P")


def handle_exception(
    func: Callable[P, T]
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """A decorator that handles exceptions. If an exception is raised, it will
    first check if it is a ClickException, which is a special exception that
    Click uses to print a message and exit. If it is not a ClickException, it
    will save the error to a file and then raise a ClickException with a
    message telling the user to report the issue on GitHub. All exceptions
    running within a function decorated with this decorator should be caught if
    they are not intended to be handled by this decorator.

    Args:
        func (Callable[P, T]): The function to decorate.

    Returns:
        Callable[[Callable[P, T]], Callable[P, T]]: The wrapper function.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, click.ClickException):
                raise e

            filepath = os.path.join(os.getcwd(), "error.txt")
            try:
                with open(filepath, "a") as f:
                    f.write(f"====================\n")
                    f.write(f"Fatal Error Occured!\n")
                    f.write(f"Date: {datetime.datetime.now()}\n")
                    f.write(f"Exception: {e}\n")
                    f.write(f"Version: {__version__}\n")
                    f.write(
                        "".join(traceback.format_exception(*sys.exc_info()))
                    )
                    f.write(f"====================\n")

                rich.print(
                    f"Saved [bold red]ERROR[/] to [bold green]{filepath}[/]"
                )

            except Exception:
                raise click.ClickException(
                    "A fatal error occurred and could not be saved to a file. "
                    + "Please report this issue on GitHub, found below this "
                    + "message. The error that occurred while trying to save "
                    + "the error to a file is below this message. Please "
                    + "attach this error to your issue."
                ) from e

            raise click.ClickException(
                "A fatal error occurred. Please report this issue on "
                + "GitHub, found below this message. Your error has been "
                + "saved to the file mentioned above. Please attach this "
                + "file to your issue."
            )

    return wrapper


class ProgressBar:
    def __init__(self, task_message: str = ""):
        """A context manager that creates a progress bar. If the silent option
        is passed, the progress bar will not be created.

        Args:
            task_message (str): The message to display in the progress bar.
                Defaults to "".
        """
        self.progress: Progress | None = None
        self.task_id: str | None = None
        self.task_message = task_message
        ctx = click.get_current_context()
        self.silent = ctx.params.get("silent", False)

    def __enter__(self) -> Callable[[int, int], None]:
        def progress_bar_callback(current: int, total: int) -> None:
            """A callback function that updates the progress bar.

            If the progress bar has not been created yet, it will create it.
            This relies on the fact that the first time this function is called
            the current value will be 0.

            Args:
                current (int): Current progress.
                total (int): Total progress.
            """
            if current == 0:
                self.progress = Progress()
                self.task_id = self.progress.add_task(
                    self.task_message, total=total
                )
                self.progress.start()
            else:
                self.progress.update(self.task_id, advance=1)

        if self.silent:
            return None
        return progress_bar_callback

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.progress:
            self.progress.stop()
            self.progress = None
