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

    @abstractmethod
    def run(self, *args, **kwargs):
        """The function that will be called when the plugin's command is
        called.

        Args:
            *args: The arguments passed to the plugin's command.
            **kwargs: The keyword arguments passed to the plugin's command.
        """
        pass
