import importlib
import pkgutil
from typing import Type

from data_zipcaster.base_plugin import BasePlugin


def discover_plugins(
    package, base_class: Type[BasePlugin]
) -> list[Type[BasePlugin]]:
    """Discovers all plugins in a package.

    Args:
        package (str): The package to search for plugins.
        base_class (Type[BasePlugin]): The base class that all plugins must
            inherit from.

    Returns:
        list[Type[BasePlugin]]: A list of all plugins in the package.
    """
    plugins = []
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
        try:
            module = importlib.import_module(
                f"{package.__name__}.{modname}.plugin"
            )
        except ModuleNotFoundError:
            continue
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if (
                isinstance(attribute, type)
                and issubclass(attribute, base_class)
                and attribute != base_class
            ):
                plugins.append(attribute())
    return plugins
