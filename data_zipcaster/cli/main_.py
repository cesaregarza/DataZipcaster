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
from data_zipcaster.importers import BaseImporter

click.rich_click.USE_RICH_MARKUP = True

BOLD = "\033[1m"
UNDERLINE = "\033[4m"
DATA_ZIPCASTER_TEXT = "[bold green]Data Zipcaster[/bold green]"

EXPORTERS = discover_plugins(exporters, BasePlugin)
IMPORTERS = discover_plugins(importers, BaseImporter)


@click.group()
def cli():
    pass


if __name__ == "__main__":
    for importer in IMPORTERS:
        importer_object = importer()
        command = importer_object.build_command(EXPORTERS)
        cli.add_command(command)
    cli()
