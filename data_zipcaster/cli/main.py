import rich_click as click

from data_zipcaster.cli import exporters, importers
from data_zipcaster.cli import styles as s
from data_zipcaster.cli.base_plugins import BaseExporter, BaseImporter
from data_zipcaster.cli.plugin_discover import discover_plugins

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.ERRORS_EPILOGUE = (
    "If you believe this is a bug, please report it at our GitHub repository: "
    + "[bold green]"
    + "https://github.com/cesaregarza/DataZipcaster"
    + "[/]"
)

BOLD = "\033[1m"
UNDERLINE = "\033[4m"
DATA_ZIPCASTER_TEXT = "[bold green]Data Zipcaster[/bold green]"

EXPORTERS = discover_plugins(exporters, BaseExporter)
IMPORTERS = discover_plugins(importers, BaseImporter)


@click.group()
@click.option("-v", "--verbose", count=True, help="Increase verbosity level.")
@click.option(
    "--silent",
    is_flag=True,
    help=(
        f"Do not show any dialogs. This will override the "
        "--verbose[-v] option."
    ),
    default=False,
)
@click.pass_context
def cli(ctx: click.Context, verbose: int, silent: bool) -> None:
    pass


def main():
    for importer in IMPORTERS:
        command = importer.build_command(EXPORTERS)
        cli.add_command(command)
    cli()


if __name__ == "__main__":
    main()
