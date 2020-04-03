"""
Application main module
"""
from aiohttp.web_app import Application
from aiohttp_apispec import validation_middleware
from event_service_lib import HealthCheck, server_runner

from uaa.infrastructure.storage.db_initializer import initialize_db
from uaa.infrastructure.storage.sql_storage import SqlStorage
from uaa.log_config import LOG_CONFIG, get_logger
from uaa.services.authentication_service import AuthService
from uaa.services.users_service import UserService
from uaa.webapp.definitions import API_VERSION, CONFIG_PATH, health_check
from uaa.webapp.middlewares import error_middleware, auth_middleware
from uaa.webapp.views import users_view, auth_view


def init_uaa(app: Application) -> Application:
    """
    Initialize the web application

    Args:
        app: configuration profile to use

    Returns: web application initialized
    """
    storage_config = app['config'].get_section('storage')

    store_client = SqlStorage(**storage_config)
    initialize_db(store_client.engine)
    app['user_service'] = UserService(store_client)
    app['auth_service'] = AuthService(app['user_service'])

    HealthCheck(app, health_check)

    users_view.setup_routes(app)
    auth_view.setup_routes(app)

    app.middlewares.append(error_middleware)
    app.middlewares.append(auth_middleware)
    app.middlewares.append(validation_middleware)

    return app


if __name__ == '__main__':
    server_runner('UAA', init_uaa, API_VERSION, CONFIG_PATH, LOG_CONFIG, get_logger)
