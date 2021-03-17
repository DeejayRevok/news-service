"""
Flower celery worker monitor module
"""
import os
from argparse import ArgumentParser
from typing import Dict, Any

from flower.command import FlowerCommand

from config import config, load_config


def args_parser(server_name: str) -> Dict[str, Any]:
    """
    Parse the required arguments to run the specified server

    Args:
        server_name: name of the server to parse args

    Returns: args parsed

    """
    arg_solver = ArgumentParser(description=f'{server_name} server')
    arg_solver.add_argument('-c', '--config', required=True, help='Configuration file path')

    return vars(arg_solver.parse_args())


if __name__ == '__main__':
    args = args_parser('Flower')
    load_config(args['config'])
    if 'RABBIT_URL_PREFIX' in os.environ:
        broker_api = 'http://{user}:{password}@{host}:15672/' + os.environ.get('RABBIT_URL_PREFIX') + '/api/'
    else:
        broker_api = 'http://{user}:{password}@{host}:15672/api/'
    broker_url = 'amqp://{user}:{password}@{host}:{port}'
    flower_command = FlowerCommand()
    if 'URL_PREFIX' in os.environ:
        flower_command.execute_from_commandline(
            ['Nlp celery monitor', '--address=0.0.0.0',
             '--broker-api=' + broker_api.format(**config.rabbit),
             '--broker=' + broker_url.format(**config.rabbit),
             '--url_prefix=' + os.environ.get('URL_PREFIX')])
    else:
        flower_command.execute_from_commandline(
            ['Nlp celery monitor', '--address=0.0.0.0',
             '--broker-api=' + broker_api.format(**config.rabbit),
             '--broker=' + broker_url.format(**config.rabbit)])
