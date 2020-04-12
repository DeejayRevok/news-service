"""
Exchange consumer module
"""
from typing import Callable

from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.exceptions import AMQPConnectionError

from news_manager.log_config import get_logger

LOGGER = get_logger()


class ExchangeConsumer:
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
        self._host = host
        self._port = int(port)
        self._user = user
        self._password = password
        self._exchange = exchange
        self._queue_name = queue_name
        self._message_callback = message_callback
        self._connection = None
        self._channel = None

    def _connect(self):
        """
        Connect the consumer with the queue provider
        """
        self._connection = BlockingConnection(
            ConnectionParameters(host=self._host,
                                 port=self._port,
                                 credentials=PlainCredentials(self._user, self._password)))

    def _initialize(self):
        """
        Initialize the consumer exchange and queue
        """
        self._channel = self._connection.channel()
        self._channel.exchange_declare(exchange=self._exchange, exchange_type='fanout', durable=True)
        self._channel.queue_declare(queue=self._queue_name, exclusive=True)
        self._channel.queue_bind(exchange=self._exchange, queue=self._queue_name)

    def test_connection(self) -> bool:
        """
        Test the connection with the queue provider

        Returns: True if the connection is successful, False otherwise

        """
        try:
            self._connect()
            return True
        except AMQPConnectionError:
            return False

    def __call__(self):
        """
        Start consuming
        """
        LOGGER.info('Starting consumer')
        self._connect()
        self._initialize()
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

    def shutdown(self):
        """
        Gracefull shutdown of the current consumer
        """
        LOGGER.info('Shutting down exchange consumer')
        self._channel.close()
        self._connection.close()
