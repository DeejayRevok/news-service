"""
Exchange publisher module
"""
import json

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

    def __call__(self, message_json: dict):
        """
        Publish the input message in the previously declared exchange

        Args:
            message_json: dictionary json like message to publish

        """
        LOGGER.info('Publishing a new message')
        self._channel.basic_publish(exchange=self._exchange, routing_key='', body=json.dumps(message_json))
