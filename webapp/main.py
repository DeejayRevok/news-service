"""
Application main module
"""
import configparser

from aiohttp.web import run_app
from aiohttp.web_app import Application
from aiohttp_apispec import setup_aiohttp_apispec
from elasticapm import Client
from elasticapm.middleware import ElasticAPM

from cron.cron_factory import initialize_crons
from infrastructure.storage.storage_factory import storage_factory
from log_config import get_logger
from services.event_service import EventService
from webapp.definitions import CONFIG_PATH, API_VERSION
from webapp.middlewares import middleware_factory
from webapp.views import events_view

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

    apm_client = Client(config={
        'SERVICE_NAME': parsed_config.get('ELASTIC_APM', 'service-name'),
        'SECRET_TOKEN': parsed_config.get('ELASTIC_APM', 'secret-token'),
        'SERVER_URL': f'http://{parsed_config.get("ELASTIC_APM", "host")}:{parsed_config.get("ELASTIC_APM", "port")}'
    })

    app['apm'] = ElasticAPM(app, apm_client)

    return app


if __name__ == '__main__':
    LOGGER.info('Starting web app')
    APPLICATION = init_app()
    run_app(APPLICATION, host=APPLICATION['host'], port=APPLICATION['port'],
            access_log=get_logger())
