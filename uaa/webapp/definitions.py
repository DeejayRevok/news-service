"""
UAA webapp definitions module
"""
from os.path import join, dirname
from typing import Callable

from aiohttp.web_exceptions import HTTPUnauthorized

from uaa.infrastructure.storage.sql_storage import SqlStorage
from uaa.lib.config_tools import parse_config

API_VERSION = 'v1'
CONFIG_PATH = join(dirname(dirname(__file__, )), 'config.ini')


async def health_check() -> bool:
    """
    Check the health status of the application

    Returns: True if the status is OK, False otherwise

    """
    app_config = parse_config(CONFIG_PATH)
    storage_config = app_config._sections['storage']
    storage = SqlStorage(**storage_config)
    return storage.health_check()


def login_required(func: Callable) -> Callable:
    """
    Decorator which checks if the there is a valid authenticated user

    Args:
        func: function to decorate

    Returns: decorated function

    """
    def wrapper(request):
        if not request.user:
            raise HTTPUnauthorized(reason='User is not present')
        return func(request)
    return wrapper
