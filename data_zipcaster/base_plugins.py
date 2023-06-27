from abc import ABC, abstractmethod, abstractproperty
from typing import Callable, ParamSpec, Type, TypeVar, cast

import rich
import rich_click as click
from typing_extensions import NotRequired, TypedDict

from data_zipcaster.cli.utils import handle_exception

T = TypeVar("T")
P = ParamSpec("P")


class BaseExporter(ABC):
    @abstractproperty
    def name(self) -> str:
        """The name of the plugin. This will be used as the command name in
        Click.

        Returns:
            str: The name of the plugin.
        """
        pass

    @abstractproperty
    def help(self) -> str:
        """The help message for the plugin. This will be used as the help
        message for the command in Click.

        Returns:
            str: The help message for the plugin.
        """
        pass

    @abstractmethod
    def do_run(self, data: dict, **kwargs):
        pass

    def vprint(self, *args, level: int = 1) -> None:
        verbose_level = click.get_current_context().obj["verbose"]
        if verbose_level >= level:
            rich.print(*args)


class BaseImporter(ABC):
    @abstractproperty
    def name(self) -> str:
        """The name of the plugin. This will be used as the command name in
        Click.

        Returns:
            str: The name of the plugin.
        """
        pass

    @abstractproperty
    def help(self) -> str:
        """The help message for the plugin. This will be used as the help
        message for the command in Click.

        Returns:
            str: The help message for the plugin.
        """
        pass

    @abstractmethod
    def do_run(self, **kwargs) -> dict:
        pass

    class Options(TypedDict):
        option_name_1: str
        option_name_2: NotRequired[str]
        type_: NotRequired[
            Type[str]
            | Type[int]
            | Type[float]
            | click.Choice
            | click.Path
            | click.FloatRange
            | click.IntRange
        ]
        is_flag: NotRequired[bool]
        help: str
        default: NotRequired[str | int | float | bool | None]
        multiple: NotRequired[bool]
        nargs: NotRequired[int]

    @property
    def has_options(self) -> bool:
        return self.get_options() is not None

    def get_options(self) -> list[Options] | None:
        """Get the options for the importer. By default, this returns None. Must
        be overridden by the importer.

        Returns:
            list[Options] | None: A list of options for the importer.
        """
        return None

    @property
    def get_option_names(self) -> list[str] | None:
        if (options := self.get_options()) is None:
            return None

        return [option["option_name_1"] for option in options]

    def parse_options(
        self, options: list[Options]
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """Decorator to parse options for a command.

        Given a list of options, this decorator will wrap the function in a
        series of click.option decorators defined by the options list.

        Args:
            options (list[Options]): A list of options to parse.

        Returns:
            Callable: The decorated function.
        """

        def parse_options_decorator(func: Callable[P, T]) -> Callable[P, T]:
            for option in options:
                option_dict = dict(option)
                # pop out the option names
                option_name_args = [option_dict.pop("option_name_1")]
                # If there is a second option name, add it to the list
                if option_name_2 := option_dict.pop("option_name_2", None):
                    option_name_args.append(option_name_2)

                # The key "type_" is reserved by Python, so we need to rename it
                # to "type" for the click.option decorator
                if "type_" in option_dict:
                    option_dict["type"] = option_dict.pop("type_")
                # Wrap the option in a click.option decorator
                wrapper = click.option(
                    *option_name_args, **option_dict  # type: ignore
                )
                func = wrapper(func)
            return func

        return parse_options_decorator

    def build_command(self, exporters: list[BaseExporter]) -> Callable[P, T]:
        out_func = handle_exception(self.run)
        out_func = click.pass_context(out_func)

        # Add options if they exist
        if (options := self.get_options()) is not None:
            out_func = self.parse_options(options)(out_func)

        # Add exporters
        out_func = click.option(
            "-e",
            "--exporter",
            type=click.Choice([exporter.name for exporter in exporters]),
            multiple=True,
            help=(
                "Which [yellow bold]exporter[/] to use. Can be specified "
                + "multiple times to export to multiple formats."
            ),
        )(out_func)

        # Save the exporter list
        self.exporters = exporters

        # Add the verbose flag
        out_func = click.option(
            "-v",
            "--verbose",
            count=True,
            help="Increase verbosity level.",
        )(out_func)

        return click.command(name=self.name, help=self.help)(out_func)

    def run(self, ctx: click.Context, *, verbose: int = 0, **kwargs) -> None:
        exporters = cast(tuple[BaseExporter, ...], kwargs.pop("exporter", None))

        if len(exporters) == 0:
            raise click.ClickException(
                "No exporters were specified. Please specify at least one "
                + "exporter with the -e/--exporter flag. Available exporters "
                + "are: "
                + "[/], [yellow bold]".join(
                    [exporter.name for exporter in self.exporters]
                )
                + ("[/]" if len(self.exporters) > 1 else "")
            )

        internal_data = self.do_run(**kwargs)

        for exporter in exporters:
            exporter.do_run(internal_data)

    def vprint(self, *args, level: int = 1) -> None:
        """Prints a message if the verbose level is greater than or equal to the
        specified level. This is a wrapper around rich.print that checks the
        verbose level. It is capped to level 3, so any level greater than 3
        will be treated as 3.

        Args:
            *args: The arguments to pass to rich.print.
            level (int): The verbose level required to print the message. If the
                current verbose level is greater than or equal to this level,
                the message will be printed. Capped at 3. Defaults to 1.
        """
        verbose_level = click.get_current_context().obj["verbose"]
        if verbose_level >= level:
            rich.print(*args)
