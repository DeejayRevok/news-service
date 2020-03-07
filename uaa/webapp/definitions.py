from os.path import join, dirname

from aiohttp.web_exceptions import HTTPUnauthorized

from uaa.infrastructure.storage.sql_storage import SqlStorage
from uaa.lib.config_tools import parse_config

API_VERSION = 'v1'
CONFIG_PATH = join(dirname(dirname(__file__, )), 'config.ini')


async def health_check():
    app_config = parse_config(CONFIG_PATH)
    storage_config = app_config._sections['storage']
    storage = SqlStorage(**storage_config)
    return storage.health_check()


def login_required(func):
    def wrapper(request):
        if not request.user:
            raise HTTPUnauthorized(reason='User is not present')
        return func(request)
    return wrapper
