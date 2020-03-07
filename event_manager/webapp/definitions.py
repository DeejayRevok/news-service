from os.path import join, dirname

from aiohttp.web_exceptions import HTTPUnauthorized

from event_manager.infrastructure.storage.storage_factory import storage_factory
from event_manager.lib.config_tools import parse_config

API_VERSION = 'v1'
CONFIG_PATH = join(dirname(dirname(__file__, )), 'config.ini')


async def health_check():
    app_config = parse_config(CONFIG_PATH)
    storage_config = app_config._sections[app_config.get('server', 'storage')]
    storage_client = storage_factory(app_config.get('server', 'storage'), storage_config)
    return storage_client.health_check()


def login_required(func):
    def wrapper(request):
        if not request.user:
            raise HTTPUnauthorized(reason='User is not present')
        return func(request)
    return wrapper
