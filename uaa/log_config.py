"""
Logging configuration
"""
from logging import config as logging_config, getLogger, DEBUG, INFO
from logging import Logger
from os import makedirs
from os.path import join, dirname, exists

import configparser


def check_dir(directory: str) -> str:
    """
    Check if the specified directory exists. If not, create it

    Args:
        directory: directory path to check

    Returns: directory path

    """
    if not exists(directory):
        makedirs(directory)
    return directory

CONFIG_PARSER = configparser.RawConfigParser()
CONFIG_PARSER.read(join(dirname(__file__), 'config.ini'))

LOG_FILE = join(check_dir(join(dirname(__file__), 'var', 'logs')), "uaa.log")

ERROR_FORMAT = "%(levelname)s at %(asctime)s in %(funcName)s in %(filename) at line %(lineno)d: %(message)s"
DEBUG_FORMAT = "%(levelname)s at line %(lineno)d in %(filename)s at %(asctime)s: %(message)s"

LOG_CONFIG = {
    'version': 1,
    'formatters': {
        'error': {'format': ERROR_FORMAT},
        'debug': {'format': DEBUG_FORMAT}},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'debug',
            'level': DEBUG
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'filename': LOG_FILE,
            'formatter': 'error',
            'level': DEBUG
        },
        'logstash': {
            'class': 'logstash.TCPLogstashHandler',
            'level': INFO,
            'host': CONFIG_PARSER.get('LOGSTASH', 'host'),
            'port': int(CONFIG_PARSER.get('LOGSTASH', 'port')),
            'version': 1
        }
    },
    'loggers': {
        'main_logger': {
            'handlers': ['console', 'file', 'logstash'],
            'level': DEBUG}
    }
}

logging_config.dictConfig(LOG_CONFIG)


def get_logger() -> Logger:
    """
    Get logger with the configuration specified above
    """
    return getLogger('main_logger')
