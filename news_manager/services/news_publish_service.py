"""
News publish service module
"""
import sys
from multiprocessing import Process

from aiohttp.web_app import Application

from news_manager.infrastructure.messaging.exchange_publisher import ExchangePublisher
from news_manager.log_config import get_logger

LOGGER = get_logger()


class NewsPublishService:
    """
    News publish service implementation
    """
    def __init__(self, app: Application):
        """
        Start a new process which listens the new inserts and publish them in the exchange configured

        Args:
            app: application associated
        """
        self._app = app
        self._news_service = app['news_service']
        self._exchange_publisher = ExchangePublisher(**app['config'].get_section('RABBIT'), exchange='news')

        if not self._exchange_publisher.test_connection():
            LOGGER.error('Error connecting to the queue provider. Exiting...')
            sys.exit(1)

        self._publish_process = Process(target=self.__call__)
        self._publish_process.start()

    def __call__(self):
        """
        Initialize the exchange publisher and start listening the database inserts

        """
        self._exchange_publisher.connect()
        self._exchange_publisher.initialize()
        try:
            for new_inserted in self._news_service.consume_new_inserts():
                LOGGER.info('Listened inserted new %s', new_inserted['title'])
                self._exchange_publisher(new_inserted)
        except Exception as exc:
            LOGGER.error('Error while consuming from storage %s', str(exc))
        except KeyboardInterrupt:
            LOGGER.info('Request to stop listening for new updates in database')

    async def shutdown(self):
        """
        Shutdown the current news publish service shutting down the exchange publisher and waiting the consume process
        to join
        """
        self._publish_process.join()
        self._exchange_publisher.shutdown()
