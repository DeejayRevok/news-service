"""
Logging configuration
"""
from logging import config as logging_config, getLogger
from logging import Logger
from os.path import join, dirname

from news_service_lib.log_utils import check_log_dir, get_base_log_config

LOG_FILE = join(check_log_dir(join(dirname(__file__), 'var', 'logs')), "nlp-service.log")
LOG_CONFIG = get_base_log_config(LOG_FILE)


def get_logger() -> Logger:
    """
    Get logger with the configuration specified above
    """
    logging_config.dictConfig(LOG_CONFIG)
    logger = getLogger('main_logger')
    logger.propagate = False
    return logger
