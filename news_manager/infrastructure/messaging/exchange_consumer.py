"""
Exchange consumer module
"""
from typing import Callable

from news_manager.infrastructure.messaging.exchange_provider import ExchangeProvider
from news_manager.log_config import get_logger

LOGGER = get_logger()


class ExchangeConsumer(ExchangeProvider):
    """
    Exchange consumer implementation
    """
    def __init__(self, host: str, port: str, user: str, password: str, exchange: str, queue_name: str,
                 message_callback: Callable):
        """
        Create a new exchange consumer with the specified configuration parameters

        Args:
            host: queue provider service host address
            port: queue provider ampq port
            user: queue provider service access user
            password: queue provider service access password
            exchange: exchange to consume from
            queue_name: name of the queue used to consume
            message_callback: consumed messages callback
        """
        LOGGER.info('Initializing exchange consumer for %s', exchange)
        super().__init__(host, port, user, password, exchange)
        self._queue_name = queue_name
        self._message_callback = message_callback

    def initialize(self):
        """
        Initialize the consumer exchange and queue
        """
        super().initialize()
        self._channel.queue_declare(queue=self._queue_name, exclusive=True)
        self._channel.queue_bind(exchange=self._exchange, queue=self._queue_name)

    def __call__(self):
        """
        Start consuming
        """
        LOGGER.info('Starting consumer')
        self.connect()
        self.initialize()
        self._channel.basic_consume(
            queue=self._queue_name, on_message_callback=self._message_callback, auto_ack=True)
        try:
            self._channel.start_consuming()
        except KeyboardInterrupt:
            LOGGER.info('Request to interrupt consuming')
            self.shutdown()
        except Exception as ex:
            LOGGER.error('Error while consuming %s', repr(ex), exc_info=True)
            self.shutdown()
