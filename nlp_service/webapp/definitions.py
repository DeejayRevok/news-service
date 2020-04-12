"""
Nlp service webapp definitions module
"""
from os.path import join, dirname

from aiohttp.web_app import Application

API_VERSION = 'v1'
CONFIG_PATH = join(dirname(dirname(__file__, )), 'configs')


async def health_check(_: Application) -> bool:
    """
    Check the health status of the web application
    Args:
        _: web application to check health

    Returns: True if the application is healthy, False otherwise

    """
    return True
