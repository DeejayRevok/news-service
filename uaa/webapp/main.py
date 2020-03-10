"""
Application main module
"""
from aio_tiny_healthcheck import Checker
from aiohttp.web import run_app
from aiohttp.web_app import Application
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware
from elasticapm import Client
from elasticapm.middleware import ElasticAPM

from uaa.infrastructure.storage.db_initializer import initialize_db
from uaa.infrastructure.storage.sql_storage import SqlStorage
from uaa.lib.config_tools import parse_config
from uaa.log_config import get_logger
from uaa.services.authentication_service import AuthService
from uaa.services.users_service import UserService
from uaa.webapp.definitions import CONFIG_PATH, health_check, API_VERSION
from uaa.webapp.middlewares import error_middleware, auth_middleware
from uaa.webapp.views import users_view, auth_view

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

    storage_config = parsed_config._sections['storage']

    store_client = SqlStorage(**storage_config)
    initialize_db(store_client.engine)
    app['user_service'] = UserService(store_client)
    app['auth_service'] = AuthService(app['user_service'])

    healthcheck_provider = Checker(success_code=200, fail_code=500)
    healthcheck_provider.add_check('health_check', health_check)
    app.router.add_get('/healthcheck', healthcheck_provider.aiohttp_handler)

    users_view.setup_routes(app)
    auth_view.setup_routes(app)

    app.middlewares.append(error_middleware)
    app.middlewares.append(auth_middleware)
    app.middlewares.append(validation_middleware)

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
