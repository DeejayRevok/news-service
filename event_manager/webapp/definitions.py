from os.path import join, dirname
from typing import Callable

from aiohttp.web_app import Application
from aiohttp.web_exceptions import HTTPUnauthorized
from aiohttp.web_request import Request

from event_manager.infrastructure.storage.storage_factory import storage_factory

API_VERSION = 'v1'
CONFIG_PATH = join(dirname(dirname(__file__, )), 'configs')


async def health_check(app: Application) -> bool:
    """
    Check the health status of the apllication checking the connection with the database

    Args:
        app: application to check health

    Returns: True if the status is OK, False otherwise

    """
    storage_config = app['config'].get_section(app['config'].get('server', 'storage'))
    storage_client = storage_factory(app['config'].get('server', 'storage'), storage_config)
    return storage_client.health_check()


def login_required(func: Callable):
    """
    Decorator used to check if the request is authenticated

    Args:
        func: function to decorate

    Returns: decorated function checking the authentication

    """
    def wrapper(request: Request):
        if not request.user:
            raise HTTPUnauthorized(reason='User is not present')
        return func(request)
    return wrapper
