"""
UAA webapp definitions module
"""
from os.path import join, dirname

from aiohttp.web_app import Application

from uaa.infrastructure.storage.sql_storage import SqlStorage

API_VERSION = 'v1'
CONFIG_PATH = join(dirname(dirname(__file__, )), 'configs')


async def health_check(app: Application) -> bool:
    """
    Check the health status of the application

    Args:
        app: application to check health

    Returns: True if the status is OK, False otherwise

    """
    storage_config = app['config'].get_section('storage')
    storage = SqlStorage(**storage_config)
    return storage.health_check()
