from abc import ABC, abstractmethod, abstractproperty
from typing import Callable, ParamSpec, Type, TypeVar

import rich_click as click
from typing_extensions import NotRequired, TypedDict

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
            str
            | int
            | float
            | click.Choice
            | click.Path
            | click.FloatRange
            | click.IntRange
        ]
        is_flag: NotRequired[bool]
        help: str
        default: NotRequired[str | int | float | bool]
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
        if self.get_options() is None:
            return None

        return [option["option_name_1"] for option in self.get_options()]

    def parse_options(self, options: list[Options]) -> Callable[P, T]:
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
                # pop out the option names
                option_name_args = [option.pop("option_name_1")]
                # If there is a second option name, add it to the list
                if option_name_2 := option.pop("option_name_2", None):
                    option_name_args.append(option_name_2)
                
                # The key "type_" is reserved by Python, so we need to rename it
                # to "type" for the click.option decorator
                if "type_" in option:
                    option["type"] = option.pop("type_")
                # Wrap the option in a click.option decorator
                func = click.option(*option_name_args, **option)(func)
            return func

        return parse_options_decorator

    def build_command(
        self, exporters: list[Type[BaseExporter]]
    ) -> Callable[P, T]:
        out_func = click.pass_context(self.do_run)

        # Add options if they exist
        if self.has_options:
            out_func = self.parse_options(self.get_options())(out_func)

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
        self.exporters = [exporter() for exporter in exporters]

        # Pass the context just in case and return the newly wrapped function
        return click.command(name=self.name, help=self.help)(out_func)

    def run(self, **kwargs) -> None:
        internal_data = self.do_run(**kwargs)

        for exporter in self.exporters:
            exporter.do_run(internal_data)
