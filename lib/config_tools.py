"""
Configuration tools module
"""
import configparser


def parse_config(config_path: str) -> configparser.RawConfigParser:
    """
    Parse the configuration from the specified path

    Args:
        config_path: configuration route

    Returns: parsed configuration

    """
    config_parser = configparser.RawConfigParser()
    config_parser.read(config_path)
    return config_parser
