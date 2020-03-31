"""
Application main module
"""
from aiohttp.web_app import Application
from event_service_lib.healthcheck import HealthCheck
from event_service_lib.server_utils import server_runner

from event_manager.cron.cron_factory import initialize_crons
from event_manager.infrastructure.storage.storage_factory import storage_factory
from event_manager.log_config import get_logger, LOG_CONFIG
from event_manager.services.event_service import EventService
from event_manager.services.uaa_service import UaaService
from event_manager.webapp.definitions import CONFIG_PATH, health_check, API_VERSION
from event_manager.webapp.middlewares import error_middleware, auth_middleware
from event_manager.webapp.views import events_view


def init_event_manager(app: Application) -> Application:
    """
    Initialize the web application

    Args:
        app: configuration profile to use

    Returns: web application initialized
    """

    storage_config = app['config'].get_section(app['config'].get('server', 'storage'))

    event_store_client = storage_factory(app['config'].get('server', 'storage'), storage_config)
    app['event_service'] = EventService(event_store_client)

    uaa_config = app['config'].get_section('UAA')
    app['uaa_service'] = UaaService(**uaa_config)

    HealthCheck(app, health_check)

    events_view.setup_routes(app)

    app.middlewares.append(error_middleware)
    app.middlewares.append(auth_middleware)

    initialize_crons(app)

    return app


if __name__ == '__main__':
    server_runner('Event manager', init_event_manager, API_VERSION, CONFIG_PATH, LOG_CONFIG, get_logger)
