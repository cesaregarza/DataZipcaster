from abc import ABC, abstractmethod, abstractproperty
from typing import Callable, ParamSpec, Type, TypeVar

T = TypeVar("T")
P = ParamSpec("P")


class BasePlugin(ABC):
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

    def run(
        self,
        **kwargs,
    ):
        """The function that will be called when the plugin's command is
        called. This function will be passed the config dictionary by default.
        Variadic arguments are not supported for Click options, so the only way
        to support arbitrary arguments is to use the config dictionary. If you
        won't be using the config dictionary, you still need to include it in
        the function signature as Click will pass it to the function by
        default.

        Args:
            config (dict[str, str]): The config dictionary. This will be passed
                to the function by default. The keys are the section names in
                the config file.
            flags (dict[str, bool]): A dictionary of the flags passed to the
                plugin's command. The keys are the flag names, and the values
                are whether or not the flag was passed.
            *args: The arguments passed to the plugin's command.
            **kwargs: The keyword arguments passed to the plugin's command.
        """

        self.do_run(**kwargs)

    @abstractmethod
    def do_run(
        self,
        config: dict[str, dict[str, str]],
        flags: dict[str, bool],
        *args,
        **kwargs,
    ):
        """The actual function that will execute the plugin's command. This
        is invoked by the ``run`` function, which functions as a wrapper for
        this function. This function will be passed the config dictionary by
        default. Variadic arguments are not supported for Click options, so the
        only way to support arbitrary arguments is to use the config dictionary.
        If you won't be using the config dictionary, you still need to include
        it in the function signature as Click will pass it to the function by
        default.

        Args:
            config (dict[str, str]): The config dictionary. This will be passed
                to the function by default. The keys are the section names in
                the config file.
            flags (dict[str, bool]): A dictionary of the flags passed to the
                plugin's command. The keys are the flag names, and the values
                are whether or not the flag was passed.
            *args: The arguments passed to the plugin's command.
            **kwargs: The keyword arguments passed to the plugin's command.
        """
        pass

    def add_exporters(
        self, exporters: list[Type["BasePlugin"]]
    ) -> Callable[P, T]:
        """Decorator to add exporters to the plugin.

        Args:
            exporters (list[Type[BasePlugin]]): A list of exporters to add to
                the plugin.

        Returns:
            Callable[P, T]: The decorated function.
        """

        for exporter in exporters:
            exporter_object = exporter()
            # TODO 6/25/2023: Finish this function. This function should run
            # after do_run and should take the output of do_run and pass it to
            # the exporters, running each exporter in the order they were
            # passed to the CLI.
