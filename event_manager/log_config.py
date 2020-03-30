"""
Logging configuration
"""
from logging import config as logging_config, getLogger
from logging import Logger
from os.path import join, dirname

from lib.sources.log_utils import get_base_log_config, check_log_dir

LOG_FILE = join(check_log_dir(join(dirname(__file__), 'var', 'logs')), "event-manager.log")
LOG_CONFIG = get_base_log_config(LOG_FILE)


def get_logger() -> Logger:
    """
    Get logger with the configuration specified above
    """
    logging_config.dictConfig(LOG_CONFIG)
    return getLogger('main_logger')
