"""
Celery tasks implementation module
"""
import asyncio
import json

from news_service_lib import NlpServiceService
from news_service_lib.models import New
from pika import BlockingConnection, ConnectionParameters, PlainCredentials

from nlp_service.log_config import get_logger
from nlp_service.nlp_celery_worker.celery_app import CELERY_APP

LOGGER = get_logger()
NLP_REMOTE_SERVICE = None
QUEUE_PROVIDER_CONFIG = None


@CELERY_APP.app.task(name='initialize_worker')
def initialize_worker(nlp_service_config: dict, queue_config: dict):
    """
    Initialize the celery worker global variables

    Args:
        nlp_service_config: configuration of the nlp microservice
        queue_config: queue provider configuration

    """
    global NLP_REMOTE_SERVICE, QUEUE_PROVIDER_CONFIG
    LOGGER.info('Initializing worker')
    if NLP_REMOTE_SERVICE is None:
        NLP_REMOTE_SERVICE = NlpServiceService(**nlp_service_config)
    else:
        LOGGER.info('Nlp service remote interface already initialized')
    if QUEUE_PROVIDER_CONFIG is None:
        QUEUE_PROVIDER_CONFIG = queue_config
    else:
        LOGGER.info('Queue config already initialized')


@CELERY_APP.app.task(name='hydrate_new_entities')
def hydrate_new_with_entities(new: dict):
    """
    Hydrate the input new with named entities

    Args:
        new: new to hydrate

    Returns: new hydrated with named entities

    """
    global NLP_REMOTE_SERVICE
    LOGGER.info('Hydrating new %s with entities', new['title'])
    if NLP_REMOTE_SERVICE is not None:
        LOGGER.info('NLP service ready. Requesting new named entities...')
        new = New(**new)
        new.entities = list(asyncio.run(NLP_REMOTE_SERVICE.get_entities(new.content)))
        return dict(new)
    else:
        LOGGER.warning('Nlp service remote interface, not initialized, skipping named entities hydrating...')
        return None


@CELERY_APP.app.task(name='publish_hydrated_new')
def publish_hydrated_new(new: dict):
    """
    Publish the the input new updated

    Args:
        new: new to publish

    """
    global QUEUE_PROVIDER_CONFIG
    if new is not None:
        LOGGER.info('Publishing hydrated new %s', new['title'])
        if QUEUE_PROVIDER_CONFIG is not None:
            LOGGER.info('Queue connection initialized, publishing...')

            new['hydrated'] = True
            connection = BlockingConnection(
                ConnectionParameters(host=QUEUE_PROVIDER_CONFIG['host'],
                                     port=int(QUEUE_PROVIDER_CONFIG['port']),
                                     credentials=PlainCredentials(QUEUE_PROVIDER_CONFIG['user'],
                                                                  QUEUE_PROVIDER_CONFIG['password'])))
            channel = connection.channel()
            channel.exchange_declare(exchange='news', exchange_type='fanout', durable=True)
            channel.basic_publish(exchange='news', routing_key='', body=json.dumps(dict(new)))

            LOGGER.info('New published')
            channel.close()
            connection.close()
        else:
            LOGGER.warning('Queue connection configuration not initialized, skipping publish...')
    else:
        LOGGER.warning('Tasks chain services not initialized, skipping publish...')
