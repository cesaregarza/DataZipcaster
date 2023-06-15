import os
import time
from typing import Callable, ParamSpec, TypeVar

import rich_click as click
import splatnet3_scraper as sn3s
from rich import print

from data_zipcaster import exporters, importers
from data_zipcaster.base_plugin import BasePlugin
from data_zipcaster.cli.config_reader import read_config
from data_zipcaster.cli.constants import FLAGS
from data_zipcaster.cli.plugin_discover import discover_plugins

click.rich_click.USE_RICH_MARKUP = True

BOLD = "\033[1m"
UNDERLINE = "\033[4m"
DATA_ZIPCASTER_TEXT = "[bold green]Data Zipcaster[/bold green]"

EXPORTERS = discover_plugins(exporters, BasePlugin)
IMPORTERS = discover_plugins(importers, BasePlugin)


@click.group(invoke_without_command=True)
@click.option(
    "--config",
    type=click.Path(exists=False, dir_okay=False),
    help=(
        "Path to the config file. If not specified, the default path is "
        + "[bold yellow]config.ini[/] in the current directory."
    ),
    default=os.path.join(os.getcwd(), "config.ini"),
)
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
    type=click.Choice([plugin.name for plugin in IMPORTERS]),
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
    config: str,
    exporter: list[str],
    importer: str,
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
            config,
            exporter,
            importer,
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
    config_path: str,
    exporter: list[str],
    importer: str,
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

    flags = {
        FLAGS.SALMON: flag_salmon,
        FLAGS.XBATTLE: flag_xbattle,
        FLAGS.TURF: flag_turf,
        FLAGS.ANARCHY: flag_anarchy,
        FLAGS.PRIVATE: flag_private,
    }

    # Get the importer
    selected_importer = [imp for imp in IMPORTERS if imp.name == importer][0]
    config = read_config(config_path)
    data = selected_importer.run(config, flags)


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
