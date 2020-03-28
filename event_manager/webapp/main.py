"""
Application main module
"""
import os

from aio_tiny_healthcheck import Checker
from aiohttp.web import run_app
from aiohttp.web_app import Application
from aiohttp_apispec import setup_aiohttp_apispec
from elasticapm import Client
from elasticapm.middleware import ElasticAPM

from event_manager.cron.cron_factory import initialize_crons
from event_manager.infrastructure.storage.storage_factory import storage_factory
from event_manager.lib.apispec_utils import setup_aiohttp_apispec_mod
from event_manager.lib.config_tools import parse_config
from event_manager.log_config import get_logger
from event_manager.services.event_service import EventService
from event_manager.services.uaa_service import UaaService
from event_manager.webapp.definitions import CONFIG_PATH, health_check, API_VERSION
from event_manager.webapp.middlewares import error_middleware, auth_middleware
from event_manager.webapp.views import events_view

LOGGER = get_logger()


def init_app() -> Application:
    """
    Initialize the web application

    Returns: web application initialized

    """
    LOGGER.info('Initializing app')
    app = Application()

    parsed_config = parse_config(CONFIG_PATH)

    app['host'] = parsed_config.get('server', 'host')
    app['port'] = int(parsed_config.get('server', 'port'))

    storage_config = parsed_config._sections[parsed_config.get('server', 'storage')]

    event_store_client = storage_factory(parsed_config.get('server', 'storage'), storage_config)
    app['event_service'] = EventService(event_store_client)

    uaa_config = parsed_config._sections['UAA']
    app['uaa_service'] = UaaService(**uaa_config)

    healthcheck_provider = Checker(success_code=200, fail_code=500)
    healthcheck_provider.add_check('health_check', health_check)
    app.router.add_get('/healthcheck', healthcheck_provider.aiohttp_handler)

    events_view.setup_routes(app)

    app.middlewares.append(error_middleware)
    app.middlewares.append(auth_middleware)

    if 'SERVER_BASEPATH' in os.environ:
        server_base_path = os.environ.get('SERVER_BASEPATH')
        setup_aiohttp_apispec_mod(
            app=app,
            title='API',
            version=API_VERSION,
            prefix=server_base_path,
            url=f'/{API_VERSION}/api/docs/swagger.json',
            swagger_path=f'/{API_VERSION}/api/docs/ui',
            static_base_url=server_base_path,
            securityDefinitions={
                'ApiKeyAuth': {'type': 'apiKey', 'name': 'X-API-Key', 'in': 'header'}
            },
        )
    else:
        setup_aiohttp_apispec(
            app=app,
            title='API',
            version=API_VERSION,
            url=f'/{API_VERSION}/api/docs/swagger.json',
            swagger_path=f'/{API_VERSION}/api/docs/ui',
            securityDefinitions={
                'ApiKeyAuth': {'type': 'apiKey', 'name': 'X-API-Key', 'in': 'header'}
            },
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
