"""
Exchange publisher module
"""
import json

from pika.exceptions import StreamLostError

from news_manager.infrastructure.messaging.exchange_provider import ExchangeProvider
from news_manager.log_config import get_logger

LOGGER = get_logger()


class ExchangePublisher(ExchangeProvider):
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
        super().__init__(host, port, user, password, exchange)
        LOGGER.info('Initializing exchange publisher for %s', exchange)

    def __call__(self, message_json: dict, reconnection: bool = False):
        """
        Publish the input message in the previously declared exchange

        Args:
            message_json: dictionary json like message to publish
            reconnection: True if the publish is been made after a reconnection, False otherwise

        """
        LOGGER.info('Publishing a new message')
        try:
            self._channel.basic_publish(exchange=self._exchange, routing_key='', body=json.dumps(message_json))
        except StreamLostError as stle:
            LOGGER.warning(f'Connection lost with queue provider. Retrying...')
            if not reconnection:
                self.connect()
                self.initialize()
                self(message_json, reconnection=True)
            else:
                LOGGER.error(f'Fatal connection error after retrying: {stle}')
                raise ConnectionError('Error connecting to queue provider after retrying')
