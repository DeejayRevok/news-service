"""
Logging related functions
"""
from logging import DEBUG, INFO
from os import makedirs
from os.path import exists

ERROR_FORMAT = "%(levelname)s at %(asctime)s in %(funcName)s in %(filename) at line %(lineno)d: %(message)s"
DEBUG_FORMAT = "%(levelname)s at line %(lineno)d in %(filename)s at %(asctime)s: %(message)s"


def get_base_log_config(log_file_name: str) -> dict:
    """
    Get the base logging configuration

    Args:
        log_file_name: name of the file to log

    Returns: dictionary based logging configuration

    """
    return {
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
                'filename': log_file_name,
                'formatter': 'error',
                'level': DEBUG
            }
        },
        'loggers': {
            'main_logger': {
                'handlers': ['console', 'file'],
                'level': DEBUG}
        }
    }


def check_log_dir(directory: str) -> str:
    """
    Check if the specified directory exists. If not, create it

    Args:
        directory: directory path to check

    Returns: directory path

    """
    if not exists(directory):
        makedirs(directory)
    return directory


def add_logstash_handler(log_config: dict, logstash_host: str, logstash_port: int):
    """
    Add the logstash handler to the specified logging with the specified logstash host and port

    Args:
        log_config: logging configuration to modify
        logstash_host: logstash service host address
        logstash_port: logstash service port

    """
    log_config['handlers']['logstash'] = {
        'class': 'logstash.TCPLogstashHandler',
        'level': INFO,
        'host': logstash_host,
        'port': logstash_port,
        'version': 1
    }
    log_config['loggers']['main_logger']['handlers'].append('logstash')
