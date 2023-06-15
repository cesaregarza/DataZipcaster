from abc import ABC, abstractmethod, abstractproperty


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

    @abstractproperty
    def requires_config(self) -> bool:
        """Whether or not the plugin requires a config file. If this is True,
        the plugin will not be loaded if the config file is not found.

        Returns:
            bool: Whether or not the plugin requires a config file.
        """
        pass

    def verify_config(self, config: dict[str, dict[str, str]]) -> bool:
        """Verifies that the config file has the required information for the
        plugin to run. This function is called before the plugin is loaded, only
        if the ``requires_config`` property is True. If this function returns
        False, the plugin will not be loaded.

        Args:
            config (dict[str, str]): The config dictionary. The keys are the
                section names in the config file.

        Returns:
            bool: Whether or not the config file has the required information
                for the plugin to run.
        """
        return self.name in config

    def run(
        self,
        config: dict[str, dict[str, str]],
        flags: dict[str, bool],
        *args,
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
        if self.requires_config and not self.verify_config(config):
            raise KeyError(
                f"The plugin {self.name} requires a config file, but the "
                + "config file does not have the required information."
            )

        self.do_run(config, flags, *args, **kwargs)

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
