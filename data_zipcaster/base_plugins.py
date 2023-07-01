import configparser
import os
from abc import ABC, abstractmethod, abstractproperty
from typing import Any, Callable, ParamSpec, Type, TypeAlias, TypeVar, cast

import rich
import rich_click as click
from typing_extensions import NotRequired, TypedDict

from data_zipcaster.cli import styles as s
from data_zipcaster.cli.utils import handle_exception
from data_zipcaster.schemas.vs_modes import VsExtractDict

T = TypeVar("T")
P = ParamSpec("P")


OptionType: TypeAlias = (  # noqa: ECE001
    Type[str]
    | Type[int]
    | Type[float]
    | Type[bool]
    | click.Choice
    | click.Path
    | click.FloatRange
    | click.IntRange
)


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
    def do_run(self, data: VsExtractDict, **kwargs) -> None:
        pass

    class ConfigKeys(TypedDict):
        key_name: str
        type_: Type[str] | Type[int] | Type[float] | Type[bool]
        help: str

    @abstractmethod
    def get_config_keys(self) -> list[ConfigKeys]:
        """A list of keys that will be read from the config file. This is used
        to check if the config file is valid and to populate the help message.

        Returns:
            list[str]: A list of keys that will be read from the config file.
        """
        pass

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
        verbose_level = click.get_current_context().params["verbose"]
        if verbose_level >= level:
            rich.print(*args)

    def get_from_context(self, key: str) -> Any | None:
        """Get a value from the context.

        Args:
            key (str): The key to get.

        Returns:
            Any | None: The value, or None if it doesn't exist.
        """
        try:
            return click.get_current_context().obj[key]
        except KeyError:
            return None

    def get_from_config(self, key: str) -> Any | None:
        """Get a value from the config.

        Args:
            key (str): The key to get.

        Raises:
            KeyError: If the key is not in the config_keys list.

        Returns:
            Any | None: The value, or None if it doesn't exist.
        """
        if key not in (
            [config_key["key_name"] for config_key in self.get_config_keys()]
        ):
            raise KeyError(
                f"The key {key} is not in the config_keys list. Please add it "
                + "to the config_keys list. This is not an error that the user "
                + "should see."
            )
        config = self.get_from_context("config")
        try:
            return config[key]  # type: ignore
        except KeyError:
            return None


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
    def do_run(self, **kwargs) -> VsExtractDict:
        """The main function for the importer. This is where the importer should
        do its work. This function should return a dictionary of data that will
        be passed to the exporters.

        Args:
            **kwargs: The keyword arguments passed to the command.

        Returns:
            VsExtractDict: A dictionary of data that will be passed to the
                exporters.
        """
        pass

    class Options(TypedDict):
        option_name_1: str
        option_name_2: NotRequired[str]
        type_: NotRequired[OptionType]
        is_flag: NotRequired[bool]
        help: str
        default: NotRequired[str | int | float | bool | None]
        multiple: NotRequired[bool]
        nargs: NotRequired[int]
        envvar: NotRequired[str]

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
        """Get the option names for the importer. By default, this returns None.

        Returns:
            list[str] | None: A list of option names for the importer.
        """
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
        """Builds the click command for the importer. This is a wrapper around
        the run function that adds an error handler, options, exporters, and
        potentially any other things that need to be added to all subclasses of
        BaseImporter.

        Args:
            exporters (list[BaseExporter]): A list of exporters to pass to the
                run function.

        Returns:
            Callable[P, T]: The click command.
        """
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
                f"Which {s.EXPORTER_COLOR}exporter[/] to use. Can be specified "
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

        # Add the no-dialog flag
        out_func = click.option(
            "--silent",
            is_flag=True,
            help=(
                "Do not show any dialogs. This will override the --verbose[-v] "
                "option."
            ),
            default=False,
        )(out_func)

        return click.command(name=self.name, help=self.help)(out_func)

    def run(self, ctx: click.Context, *, verbose: int = 0, **kwargs) -> None:
        """The main function for the importer. This is what's called when the
        command is run. This function will call the do_run function and pass the
        data to the exporters.

        Args:
            ctx (click.Context): The click context.
            verbose (int): The verbose level. Defaults to 0.
            **kwargs: The keyword arguments passed to the command. This will
                include the options specified by the user.

        Raises:
            ClickException: If no exporters were specified. This is a
                non-fatal error that will not trigger the error handler.
        """
        exporters_string = cast(tuple[str, ...], kwargs.pop("exporter", None))
        exporters = [
            exporter
            for exporter in self.exporters
            if exporter.name in exporters_string
        ]

        if len(exporters) == 0:
            raise click.ClickException(
                "No exporters were specified. Please specify at least one "
                + "exporter with the -e/--exporter flag. Available exporters "
                + "are: "
                + f"[/], {s.EXPORTER_COLOR}".join(
                    [exporter.name for exporter in self.exporters]
                )
                + ("[/]" if len(self.exporters) > 1 else "")
            )

        self.read_config()
        self.set_options()
        internal_data = self.do_run(**kwargs)

        for exporter in exporters:
            exporter.do_run(internal_data)

    def vprint(self, *args, level: int = 1, **kwargs) -> None:
        """Prints a message if the verbose level is greater than or equal to the
        specified level. This is a wrapper around rich.print that checks the
        verbose level. It is capped to level 3, so any level greater than 3
        will be treated as 3.

        Args:
            *args: The arguments to pass to rich.print.
            level (int): The verbose level required to print the message. If the
                current verbose level is greater than or equal to this level,
                the message will be printed. Capped at 3. Defaults to 1.
            **kwargs: The keyword arguments to pass to rich.print.
        """
        ctx = click.get_current_context()
        silent = ctx.params["silent"]
        if silent:
            return

        verbose_level = ctx.params["verbose"]
        if verbose_level >= level:
            rich.print(*args, **kwargs)

    def warn(self, *args, **kwargs) -> None:
        """Prints a warning message. This is a wrapper around vprint that
        prints the message with a warning style.

        Args:
            *args: The arguments to pass to rich.print.
            **kwargs: The keyword arguments to pass to rich.print.
        """
        # Pop the level keyword argument so it doesn't get passed to vprint
        kwargs.pop("level", None)
        self.vprint(s.WARNING_COLOR + "WARNING:[/]", *args, level=0, **kwargs)

    def get_from_context(self, key: str) -> Any | None:
        """Get a value from the context.

        Args:
            key (str): The key to get.

        Returns:
            Any | None: The value, or None if it doesn't exist.
        """
        try:
            return click.get_current_context().obj[key]
        except (KeyError, TypeError):
            return None

    def read_config(self) -> None:
        """Reads the config file and saves it to the context. This will save the
        config to the context under the key "config". If the config file does
        not exist, this will print a message to the user suggesting that they
        create a config file.
        """
        ctx = click.get_current_context()
        config_path = ctx.params["config"]
        # If the file doesn't exist, raise an error suggesting the user to
        # create a config file
        if not os.path.exists(config_path):
            self.warn(
                "Config file does not exist, please consider "
                f"creating one via the {s.COMMAND_COLOR}config[/] command.",
            )
            return
        config = configparser.ConfigParser()
        config.read(config_path)
        ctx.ensure_object(dict)

        ctx.obj["config"] = config

    def get_from_config(self, key: str) -> Any | None:
        """Get a value from the config file. The list of valid keys is
        determined by the importer's options.

        Args:
            key (str): The key to get.

        Raises:
            KeyError: If the key is not a valid option for this importer.

        Returns:
            Any | None: The value, or None if it doesn't exist.
        """
        ctx = click.get_current_context()
        if key not in ctx.params.keys():
            raise KeyError(
                f"The key {key} is not a valid option for this importer. "
                "Please check the --help for a list of valid options."
            )
        config = self.get_from_context("config")
        try:
            return config[key]  # type: ignore
        except KeyError:
            return None

    def set_options(self) -> None:
        """Set the options for this importer. This will grab the options defined
        in the config file and validate them. If the config file contains an
        invalid option, a warning will be printed to the user and the default
        value will be used instead. The config value has a priority over the
        default value, but not over any other value specified by the user.
        """
        ctx = click.get_current_context()
        config = cast(
            configparser.ConfigParser, self.get_from_context("config")
        )
        if config is None:
            return

        param_map = {
            param.human_readable_name: param for param in ctx.command.params
        }
        bad_options: list[str] = []
        for key, value in config.items(self.name):
            # Check if the key is a valid option
            key_name = key.replace("-", "_")
            if key_name not in ctx.params.keys():
                self.warn(
                    f"The config file contains an invalid option, "
                    f"{s.OPTION_COLOR}{key}[/] for the importer "
                    f"{s.IMPORTER_COLOR}{self.name}[/]. "
                    "Please check the config file and remove this option.",
                )
                continue
            # Check if the value is a valid option for this key
            given_option = param_map[key_name]
            try:
                out_value = given_option.type_cast_value(ctx, value)
            except click.BadParameter:
                bad_options.append(key)
                continue

            # Set the option if the source is default
            param_source = ctx.get_parameter_source(key_name)
            if param_source is None:
                continue
            if param_source.name == "DEFAULT":
                ctx.params[key_name] = out_value

        if len(bad_options) > 0:
            self.warn(
                f"The config file contains invalid values for the following "
                f"options: {s.OPTION_COLOR}{', '.join(bad_options)}[/]. "
                "Please check the config file and correct these values, the "
                "default values will be used for now.",
            )
        return None
