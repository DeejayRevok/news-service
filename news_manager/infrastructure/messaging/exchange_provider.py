from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.exceptions import AMQPConnectionError

from news_manager.log_config import get_logger

LOGGER = get_logger()


class ExchangeProvider:

    def __init__(self, host: str, port: str, user: str, password: str, exchange: str):
        """
       Initialize the exchange provider with the specified configuration parameters

       Args:
           host: exchange provider host address
           port: exchange provider service port
           user: exchange provider access user
           password: exchange provider access password
           exchange: name of the exchange to manage
       """
        LOGGER.info('Initializing exchange publisher for %s', exchange)
        self._host = host
        self._port = int(port)
        self._user = user
        self._password = password
        self._exchange = exchange
        self._connection = None
        self._channel = None

    def connect(self):
        """
        Connect with the exchange provider
        """
        self._connection = BlockingConnection(
            ConnectionParameters(host=self._host,
                                 port=self._port,
                                 credentials=PlainCredentials(self._user, self._password)))

    def initialize(self):
        """
        Initialize the exchange provider connecting it and declaring the exchange
        """
        self._channel = self._connection.channel()
        self._channel.exchange_declare(exchange=self._exchange, exchange_type='fanout', durable=True)

    def test_connection(self) -> bool:
        """
        Test the connection with the exchange provider

        Returns: True if the connection is successful, False otherwise

        """
        try:
            self.connect()
            return True
        except AMQPConnectionError:
            return False

    def shutdown(self):
        """
        Graceful shutdown of the exchange provider
        """
        LOGGER.info('Shutting down exchange provider')
        self._channel.close()
        self._connection.close()
