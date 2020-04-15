"""
Flower celery worker monitor module
"""
import os

from flower.command import FlowerCommand
from news_service_lib import profile_args_parser, Configuration, ConfigProfile

from nlp_service.webapp.definitions import CONFIG_PATH

if __name__ == '__main__':
    args = profile_args_parser('NLP Celery worker')
    configuration = Configuration(ConfigProfile[args['profile']], CONFIG_PATH)
    if 'RABBIT_URL_PREFIX' in os.environ:
        broker_api = 'http://{user}:{password}@{host}:15672/' + os.environ.get('RABBIT_URL_PREFIX') + '/api/'
    else:
        broker_api = 'http://{user}:{password}@{host}:15672/api/'
    broker_url = 'amqp://{user}:{password}@{host}:{port}'
    flower_command = FlowerCommand()
    if 'URL_PREFIX' in os.environ:
        flower_command.execute_from_commandline(
            ['Nlp celery monitor', '--address=0.0.0.0',
             '--broker-api=' + broker_api.format(**configuration.get_section('RABBIT')),
             '--broker=' + broker_url.format(**configuration.get_section('RABBIT')),
             '--url_prefix=' + os.environ.get('URL_PREFIX')])
    else:
        flower_command.execute_from_commandline(
            ['Nlp celery monitor', '--address=0.0.0.0',
             '--broker-api=' + broker_api.format(**configuration.get_section('RABBIT')),
             '--broker=' + broker_url.format(**configuration.get_section('RABBIT'))])
