"""
News consumer module
"""
import asyncio
import sys
from multiprocessing import Process
import json

from aiohttp.web_app import Application
from news_service_lib.models import New, NamedEntity

from news_manager.infrastructure.messaging.exchange_consumer import ExchangeConsumer
from news_manager.log_config import get_logger

LOGGER = get_logger()


class NewsConsumeService:
    """
    News consumer service implementation
    """

    def __init__(self, app: Application):
        """
        Initialize the news consume service for the specified app

        Args:
            app: application associated
        """
        LOGGER.info('Starting news consumer service')
        self._app = app
        self._news_service = app['news_service']
        self._exchange_consumer = ExchangeConsumer(**app['config'].get_section('RABBIT'), exchange='new-updates',
                                                   queue_name='news_updates',
                                                   message_callback=self.new_update)

        if not self._exchange_consumer.test_connection():
            LOGGER.error('Error connecting to the queue provider. Exiting...')
            sys.exit(1)

        self._consume_process = Process(target=self._exchange_consumer.__call__)
        self._consume_process.start()

    def new_update(self, _, __, ___, body: str):
        """
        Update a new with the received data

        Args:
            body: message body with the updated new

        """
        LOGGER.info('Updating new')
        self._app['apm'].client.begin_transaction('consume')
        try:
            body = json.loads(body)
            updated_new = New(title=body['title'],
                              content=body['content'],
                              source=body['source'],
                              date=body['date'],
                              hydrated=body['hydrated'],
                              summary=body['summary'],
                              sentiment=body['sentiment'],
                              entities=[NamedEntity(**entity) for entity in body['entities']])
            asyncio.run(self._news_service.save_new(updated_new))
            self._app['apm'].client.end_transaction('New update', 'OK')
        except Exception as ex:
            LOGGER.error('Error while updating new %s', str(ex), exc_info=True)
            self._app['apm'].client.end_transaction('New update', 'FAIL')
            self._app['apm'].client.capture_exception()

    async def shutdown(self):
        """
        Shutdown the news consumer service
        """
        LOGGER.info('Shutting down news consumer service')
        self._exchange_consumer.shutdown()
        self._consume_process.join()
