"""
News publish service module
"""
from multiprocessing import Process

from news_manager.infrastructure.messaging.exchange_publisher import ExchangePublisher
from news_manager.infrastructure.storage.storage import Storage
from news_manager.log_config import get_logger

LOGGER = get_logger()


class NewsPublishService:
    """
    News publish service implementation
    """
    def __init__(self, storage_client: Storage, exchange_config: dict):
        """
        Start a new process which listens the new inserts and publish them in the exchange configured

        Args:
            storage_client: storage client to get the database consumer
            exchange_config: configuration of the exchange provider
        """
        self._exchange_publisher = ExchangePublisher(**exchange_config, exchange='news')
        self._storage_client = storage_client
        self._publish_process = Process(target=self.__call__)
        self._publish_process.start()

    def __call__(self):
        """
        Initialize the exchange publisher and start listening the database inserts

        """
        self._exchange_publisher.initialize()
        try:
            for new_inserted in self._storage_client.consume_inserts():
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
