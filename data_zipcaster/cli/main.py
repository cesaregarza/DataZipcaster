import os
import time
from typing import Callable, ParamSpec, TypeVar

import rich_click as click
from rich import print

click.rich_click.USE_RICH_MARKUP = True

BOLD = "\033[1m"
UNDERLINE = "\033[4m"
DATA_ZIPCASTER_TEXT = "[bold green]Data Zipcaster[/bold green]"


@click.group(invoke_without_command=True)
@click.option(
    "-e",
    "--exporter",
    type=str,
    required=True,
    help=(
        "Which [yellow bold]exporter[/] to use. Can be specified multiple times"
        + " to export to multiple formats."
    ),
    multiple=True,
)
@click.option(
    "-i",
    "--importer",
    type=str,
    required=True,
    help="Which [yellow bold]importer[/] to use. Can only be specified once.",
    default="splatnet",
)
@click.option(
    "-s", is_flag=True, help="Import and Export Salmon Run data.", default=False
)
@click.option(
    "-x", is_flag=True, help="Import and Export XBattle data.", default=False
)
@click.option(
    "-t", is_flag=True, help="Import and Export Turf War data.", default=False
)
@click.option(
    "-n", is_flag=True, help="Import and Export Anarchy data.", default=False
)
@click.option(
    "-p",
    is_flag=True,
    help="Import and Export Private match data.",
    default=False,
)
@click.option(
    "-a",
    is_flag=True,
    help="Import and Export [bold]ALL[/bold] data.",
    default=False,
)
@click.option(
    "-m",
    "--monitor",
    is_flag=True,
    help="Monitor the data source for new data.",
    default=False,
)
@click.option(
    "-d",
    "--delay",
    type=int,
    help=(
        "Delay between each check for new data, in seconds. "
        + "Only works with -m/--monitor, and defaults to 5 minutes."
    ),
    default=5 * 60,
)
@click.pass_context
def main(
    ctx: click.Context,
    export: list[str],
    ingest: str,
    s: bool,
    x: bool,
    t: bool,
    n: bool,
    p: bool,
    a: bool,
    monitor: bool,
    delay: int,
) -> None:
    """
    [bold green]Data Zipcaster[/] is a tool for importing and exporting
    [bold blue]Splatoon 3[/] data from various sources. It is designed to be
    modular, so that it can be easily extended to support new sources and
    formats.
    """
    if ctx.invoked_subcommand is None:
        __main(
            ctx,
            export,
            ingest,
            s,
            x,
            t,
            n,
            p,
            a,
            monitor,
            delay,
        )
    else:
        return


def __main(
    ctx: click.Context,
    export: list[str],
    import_: str,
    s: bool,
    x: bool,
    t: bool,
    n: bool,
    p: bool,
    a: bool,
    monitor: bool,
    delay: int,
) -> None:
    # Rename variables for clarity
    flag_all = a
    flag_salmon = s
    flag_xbattle = x
    flag_turf = t
    flag_anarchy = n
    flag_private = p

    # Manage flags
    (
        flag_all,
        flag_salmon,
        flag_xbattle,
        flag_turf,
        flag_anarchy,
        flag_private,
    ) = manage_flags(
        flag_all,
        flag_salmon,
        flag_xbattle,
        flag_turf,
        flag_anarchy,
        flag_private,
    )


def manage_flags(
    flag_all: bool,
    flag_salmon: bool,
    flag_xbattle: bool,
    flag_turf: bool,
    flag_anarchy: bool,
    flag_private: bool,
) -> tuple[bool, bool, bool, bool, bool, bool]:
    # This will be True if all is True, or if all the flags are True
    flag_all = (flag_all) or all(
        [flag_salmon, flag_xbattle, flag_turf, flag_anarchy, flag_private]
    )

    # If all the flags are false, then set all to True
    if not any(
        [flag_salmon, flag_xbattle, flag_turf, flag_anarchy, flag_private]
    ):
        flag_all = True

    # If all is True, then set all the flags to True
    if flag_all:
        flag_salmon = True
        flag_xbattle = True
        flag_turf = True
        flag_anarchy = True
        flag_private = True

    return (
        flag_all,
        flag_salmon,
        flag_xbattle,
        flag_turf,
        flag_anarchy,
        flag_private,
    )
