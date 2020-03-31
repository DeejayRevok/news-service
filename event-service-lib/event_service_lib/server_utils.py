"""
Server utilities functions
"""
import os
from argparse import ArgumentParser
from collections import Callable

from aiohttp.web import run_app
from aiohttp.web_app import Application
from aiohttp_apispec import setup_aiohttp_apispec
from elasticapm import Client
from elasticapm.middleware import ElasticAPM
from event_service_lib.apispec_utils import setup_aiohttp_apispec_mod
from event_service_lib.config import ConfigProfile, Configuration
from event_service_lib.log_utils import add_logstash_handler


def initialize_server(config_profile: ConfigProfile, config_path: str, log_config: dict) -> Application:
    """
    Initialize the server creating the server application with the specified configuration profile and logging config

    Args:
        config_profile: server configuration profile
        config_path: server configuration path
        log_config: server logging configuration

    Returns: server application preconfigured

    """
    app = Application()

    configuration = Configuration(config_profile, config_path)
    app['config'] = configuration

    add_logstash_handler(log_config, configuration.get('LOGSTASH', 'host'), int(configuration.get('LOGSTASH', 'port')))

    app['host'] = configuration.get('server', 'host')
    app['port'] = int(configuration.get('server', 'port'))

    return app


def finish_server_startup(app: Application, api_version: str) -> Application:
    """
    Finish the server application configuration

    Args:
        app: application to finish configuration
        api_version: api version of the server

    Returns: server application fully configured

    """
    if 'SERVER_BASEPATH' in os.environ:
        server_base_path = os.environ.get('SERVER_BASEPATH')
        setup_aiohttp_apispec_mod(
            app=app,
            title='API',
            version=api_version,
            prefix=server_base_path,
            url=f'/{api_version}/api/docs/swagger.json',
            swagger_path=f'/{api_version}/api/docs/ui',
            static_base_url=server_base_path,
            securityDefinitions={
                'ApiKeyAuth': {'type': 'apiKey', 'name': 'X-API-Key', 'in': 'header'}
            },
        )
    else:
        setup_aiohttp_apispec(
            app=app,
            title='API',
            version=api_version,
            url=f'/{api_version}/api/docs/swagger.json',
            swagger_path=f'/{api_version}/api/docs/ui',
            securityDefinitions={
                'ApiKeyAuth': {'type': 'apiKey', 'name': 'X-API-Key', 'in': 'header'}
            },
        )

    apm_client = Client(config={
        'SERVICE_NAME': app['config'].get('ELASTIC_APM', 'service-name'),
        'SECRET_TOKEN': app['config'].get('ELASTIC_APM', 'secret-token'),
        'SERVER_URL': f'http://{app["config"].get("ELASTIC_APM", "host")}:{app["config"].get("ELASTIC_APM", "port")}'
    })

    app['apm'] = ElasticAPM(app, apm_client)
    return app


def server_runner(server_name: str, server_initializer: Callable, server_api_version: str, server_config_path: str,
                  server_log_config: dict, server_logger_provider: Callable):
    """
    Run a new server with the specified name, api version and configuration, using the specified server initialization
    function

    Args:
        server_name: name of the server to run
        server_initializer: initializer function for the server application
        server_api_version: server API version
        server_config_path: configuration path of the server app
        server_log_config: server logging configuration
        server_logger_provider: server logger provider function

    """
    arg_solver = ArgumentParser(description=f'{server_name} server')
    arg_solver.add_argument('-p', '--profile', required=False, help='Configuration profile', default='LOCAL')

    args = vars(arg_solver.parse_args())

    app = finish_server_startup(
        server_initializer(initialize_server(ConfigProfile[args['profile']], server_config_path, server_log_config)),
        server_api_version)

    run_app(app, host=app['host'], port=app['port'],
            access_log=server_logger_provider())
