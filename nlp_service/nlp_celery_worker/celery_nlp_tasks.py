"""
Celery tasks implementation module
"""
import asyncio
import json
from typing import Tuple

from news_service_lib import NlpServiceService
from news_service_lib.models import New, NamedEntity
from pika import BlockingConnection, ConnectionParameters, PlainCredentials

from nlp_service.log_config import get_logger
from nlp_service.nlp_celery_worker.celery_app import CELERY_APP
from nlp_service.nlp_celery_worker.nlp_helpers.sentiment_analyzer import SentimentAnalyzer
from nlp_service.nlp_celery_worker.nlp_helpers.summarizer import generate_summary_from_sentences

LOGGER = get_logger()
NLP_REMOTE_SERVICE = None
QUEUE_PROVIDER_CONFIG = None
SENTIMENT_ANALYZER = None


@CELERY_APP.app.task(name='initialize_worker')
def initialize_worker(nlp_service_config: dict, queue_config: dict):
    """
    Initialize the celery worker global variables

    Args:
        nlp_service_config: configuration of the nlp microservice
        queue_config: queue provider configuration

    """
    global NLP_REMOTE_SERVICE, QUEUE_PROVIDER_CONFIG, SENTIMENT_ANALYZER
    LOGGER.info('Initializing worker')
    if NLP_REMOTE_SERVICE is None:
        NLP_REMOTE_SERVICE = NlpServiceService(**nlp_service_config)
    else:
        LOGGER.info('Nlp service remote interface already initialized')
    if QUEUE_PROVIDER_CONFIG is None:
        QUEUE_PROVIDER_CONFIG = queue_config
    else:
        LOGGER.info('Queue config already initialized')
    if SENTIMENT_ANALYZER is None:
        SENTIMENT_ANALYZER = SentimentAnalyzer()
    else:
        LOGGER.info('Sentiment analyzer already initialized')


@CELERY_APP.app.task(name='process_content')
def process_content(new: dict):
    """
    Apply NLP processing to the input new content

    Args:
        new: new to process content

    Returns: new to hydrate in next tasks, processed new content

    """
    global NLP_REMOTE_SERVICE
    LOGGER.info('NLP Processing new %s', new['title'])
    if NLP_REMOTE_SERVICE is not None:
        LOGGER.info('NLP service ready. Requesting NLP processing...')
        processed_content = asyncio.run(NLP_REMOTE_SERVICE.process_text(new['content']))
        return new, dict(processed_content)
    else:
        LOGGER.warning('Nlp service remote interface, not initialized, skipping named entities hydrating...')
        return None, None


@CELERY_APP.app.task(name='hydrate_new_entities')
def hydrate_new_with_entities(new_nlp_doc: Tuple[dict, dict]):
    """
    Hydrate the input new with named entities

    Args:
        new_nlp_doc: new to hydrate, NLP data about the new content

    Returns: new hydrated with named entities, processed new content

    """
    new, nlp_doc = new_nlp_doc
    LOGGER.info('Hydrating new %s with entities', new['title'])
    if nlp_doc is not None:
        new = New(**new)
        new.entities = list(
            set(map(lambda entity: NamedEntity(text=entity[0].lower(), type=entity[1]), nlp_doc['named_entities'])))
        return dict(new), nlp_doc
    else:
        LOGGER.warning('Processed new content is missing, skipping entities hydrate')
        return None


@CELERY_APP.app.task(name='hydrate_new_summary')
def hydrate_new_summary(new_nlp_doc: Tuple[dict, dict]):
    """
    Hydrate the input new with the content summary

    Args:
        new_nlp_doc: new to hydrate, NLP data about the new content

    Returns: new hydrated with the summary

    """
    new, nlp_doc = new_nlp_doc
    LOGGER.info('Hydrating new %s with the content summary', new['title'])
    if nlp_doc is not None:
        new = New(**new)
        new.summary = generate_summary_from_sentences(nlp_doc['sentences'])
        return dict(new), nlp_doc
    else:
        LOGGER.warning('Processed new content is missing, skipping summary hydrate')
        return None


@CELERY_APP.app.task(name='hydrate_new_sentiment')
def hydrate_new_sentiment(new_nlp_doc: Tuple[dict, dict]):
    """
    Hydrate the input new with the overall content sentiment

    Args:
        new_nlp_doc: new to hydrate, NLP data about the new content

    Returns: new hydrated with the sentiment

    """
    global SENTIMENT_ANALYZER
    new, nlp_doc = new_nlp_doc
    LOGGER.info('Hydrating new %s with the overall sentiment', new['title'])
    if SENTIMENT_ANALYZER is not None:
        if nlp_doc is not None:
            new = New(**new)
            new.sentiment = SENTIMENT_ANALYZER(nlp_doc['sentences'])
            return dict(new)
        else:
            LOGGER.warning('Processed new content is missing, skipping sentiment hydrate')
            return None
    else:
        LOGGER.warning('Sentiment analyzer not initialized, skipping sentiment hydrate')
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
