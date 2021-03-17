"""
Application configuration module
"""
from dynaconf.base import Settings
from dynaconf.loaders import settings_loader

config = Settings()


def load_config(config_file: str):
    """
    Load the configuration from the given file

    Args:
        config_file: name of the profile to search for the configuration

    """
    settings_loader(config, filename=config_file)
