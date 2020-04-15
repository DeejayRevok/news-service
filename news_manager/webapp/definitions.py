"""
News manager webapp definitions module
"""
from os.path import join, dirname

from aiohttp.web_app import Application

from news_manager.infrastructure.storage.storage_factory import storage_factory

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
