"""
Application main module
"""
from aiohttp.web_app import Application
from aiohttp_apispec import validation_middleware
from news_service_lib import server_runner, get_uaa_service, uaa_auth_middleware, HealthCheck

from nlp_service.nlp_celery_worker.celery_app import CELERY_APP
from nlp_service.log_config import LOG_CONFIG, get_logger
from nlp_service.nlp_celery_worker.celery_nlp_tasks import initialize_worker
from nlp_service.services.nlp_service import NlpService
from nlp_service.webapp.definitions import API_VERSION, CONFIG_PATH, health_check
from nlp_service.webapp.middlewares import error_middleware
from nlp_service.webapp.views import nlp_view


def init_nlp_service(app: Application) -> Application:
    """
    Initialize the web application

    Args:
        app: configuration profile to use

    Returns: web application initialized
    """
    uaa_config = app['config'].get_section('UAA')
    app['uaa_service'] = get_uaa_service(uaa_config)

    app['nlp_service'] = NlpService()

    HealthCheck(app, health_check)

    nlp_view.setup_routes(app)

    CELERY_APP.configure(app['config'].get_section('RABBIT'), int(app['config'].get('CELERY', 'concurrency')))

    for _ in range(int(app['config'].get('CELERY', 'concurrency'))):
        initialize_worker.delay(app['config'].get_section('SELF_REMOTE'), app['config'].get_section('RABBIT'))

    app.middlewares.append(error_middleware)
    app.middlewares.append(uaa_auth_middleware)
    app.middlewares.append(validation_middleware)

    return app


if __name__ == '__main__':
    server_runner('Nlp service', init_nlp_service, API_VERSION, CONFIG_PATH, LOG_CONFIG, get_logger)
