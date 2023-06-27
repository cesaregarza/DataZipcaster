import importlib
import pkgutil
from typing import Type, TypeVar


T = TypeVar("T")


def discover_plugins(package, base_class: Type[T]) -> list[T]:
    """Discovers all plugins in a package.

    Args:
        package (str): The package to search for plugins.
        base_class (Type[T]): The base class that all plugins inherit from.

    Returns:
        list[T]: A list of the plugins, already instantiated.
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
