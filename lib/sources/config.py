"""
Configuration tools module
"""
import configparser
from enum import Enum
from os.path import join


class ConfigProfile(Enum):
    """
    Configuration profile enum:
        - DOCKER: Docker environment app configuration
        - LOCAL: Local environment app configuration
    """
    DOCKER = 'config_docker.ini'
    LOCAL = 'config_local.ini'


class Configuration:
    """
    App configuration parser
    """

    def __init__(self, config_profile: ConfigProfile, config_folder: str):
        """
        Initialize configuration parser

        Args:
            config_profile: configuration profile
            config_folder: folder where the configurations are stored
        """

        self._config_parser = configparser.RawConfigParser()
        self._config_parser.read(join(config_folder, config_profile.value))

    def get(self, section: str, property_key: str) -> str:
        """
        Get the configuration value for the specified key and section

        Args:
            section: section to get value
            property_key: key of the configuration value to get

        Returns: configuration value
        """
        return self._config_parser.get(section, property_key)

    def get_section(self, section: str) -> dict:
        """
        Get the configuration values of the specified section

        Args:
            section: section to get config

        Returns: configuration value dict
        """
        return self._config_parser._sections[section]
