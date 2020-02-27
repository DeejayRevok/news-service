"""
Application main module
"""
import configparser
from os.path import dirname, join

from aiohttp.web import run_app
from aiohttp.web_app import Application
from aiohttp_apispec import setup_aiohttp_apispec

from cron.cron_factory import initialize_crons
from infrastructure.storage.storage_factory import storage_factory
from log_config import get_logger
from services.event_service import EventService
from webapp.middlewares import middleware_factory
from webapp.views import events_view

API_VERSION = 'v1'
CONFIG_PATH = join(dirname(dirname(__file__, )), 'config.ini')
LOGGER = get_logger()


def parse_config() -> configparser.RawConfigParser:
    """
    Parse the application configuration

    Returns: application configuration

    """
    LOGGER.info('Loading configuration')
    config_parser = configparser.RawConfigParser()
    config_parser.read(CONFIG_PATH)
    return config_parser


def init_app() -> Application:
    """
    Initialize the web application

    Returns: web application initialized

    """
    LOGGER.info('Initializing app')
    app = Application()

    parsed_config = parse_config()

    app['host'] = parsed_config.get('server', 'host')
    app['port'] = int(parsed_config.get('server', 'port'))

    storage_config = parsed_config._sections[parsed_config.get('server', 'storage')]

    event_store_client = storage_factory(parsed_config.get('server', 'storage'), storage_config)
    app['event_service'] = EventService(event_store_client)

    events_view.setup_routes(app)

    app.middlewares.append(middleware_factory)

    setup_aiohttp_apispec(
        app=app,
        title='API',
        version=API_VERSION,
        url=f'/{API_VERSION}/api/docs/swagger.json',
        swagger_path=f'/{API_VERSION}/api/docs/ui',
    )

    initialize_crons(app)

    return app


if __name__ == '__main__':
    LOGGER.info('Starting web app')
    APPLICATION = init_app()
    run_app(APPLICATION, host=APPLICATION['host'], port=APPLICATION['port'],
            access_log=get_logger())
