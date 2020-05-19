"""
Exchange publisher module
"""
import json

from pika import BlockingConnection, ConnectionParameters, PlainCredentials

from news_manager.log_config import get_logger

LOGGER = get_logger()


class ExchangePublisher:
    """
    Exchange publisher implementation
    """
    def __init__(self, host: str, port: str, user: str, password: str, exchange: str):
        """
        Initialize the exchange publisher with the specified exchange provider configuration parameters

        Args:
            host: exchange provider host address
            port: exchange provider service port
            user: exchange provider access user
            password: exchange provider access password
            exchange: name of the exchange to publish in
        """
        LOGGER.info('Initializing exchange publisher for %s', exchange)
        self._host = host
        self._port = int(port)
        self._user = user
        self._password = password
        self._exchange = exchange
        self._connection = None
        self._channel = None

    def initialize(self):
        """
        Initialize the exchange publisher connecting to the exchange provider and declaring the exchange
        """
        self._connection = BlockingConnection(
            ConnectionParameters(host=self._host,
                                 port=self._port,
                                 credentials=PlainCredentials(self._user, self._password)))
        self._channel = self._connection.channel()
        self._channel.exchange_declare(exchange=self._exchange, exchange_type='fanout', durable=True)

    def __call__(self, message_json: dict):
        """
        Publish the input message in the previously declared exchange

        Args:
            message_json: dictionary json like message to publish

        """
        LOGGER.info('Publishing new')
        self._channel.basic_publish(exchange=self._exchange, routing_key='', body=json.dumps(message_json))

    def shutdown(self):
        """
        Gracefull shutdown of the current publisher
        """
        LOGGER.info('Shutting down exchange publisher')
        self._channel.close()
        self._connection.close()
