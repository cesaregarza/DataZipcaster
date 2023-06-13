import configparser
import logging


def read_config(config_path: str) -> dict:
    """Reads the config file and returns a dictionary of the values in the
    config file. The importer and exporter names are used as the section names
    in the config file. Misc. values are stored in the "misc" section.

    Args:
        config_path (str): The path to the config file.

    Returns:
        dict: A dictionary of the values in the config file.
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    config_dict = {}
    for section in config.sections():
        config_dict[section] = {}
        for key in config[section]:
            config_dict[section][key] = config[section][key]
    return config_dict
