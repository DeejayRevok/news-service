"""
Exchange publisher tests module
"""
import json
from unittest import TestCase
from unittest.mock import patch, MagicMock

from news_manager.infrastructure.messaging.exchange_publisher import ExchangePublisher


class TestExchangePublisher(TestCase):
    """
    Exchange publisher test cases implementation
    """
    TEST_HOST = 'test_host'
    TEST_PORT = '0'
    TEST_USER = 'test_user'
    TEST_PASSWORD = 'test_password'
    TEST_EXCHANGE = 'test_exchange'
    TEST_JSON = {'test': 'test'}

    def setUp(self):
        """
        Set up the publisher instance to test
        """
        self.publisher = ExchangePublisher(self.TEST_HOST, self.TEST_PORT, self.TEST_USER, self.TEST_PASSWORD,
                                           self.TEST_EXCHANGE)

    @patch('news_manager.infrastructure.messaging.exchange_provider.ConnectionParameters')
    @patch('news_manager.infrastructure.messaging.exchange_provider.PlainCredentials')
    @patch('news_manager.infrastructure.messaging.exchange_provider.BlockingConnection')
    def test_publish(self, connection_mock, _, __):
        """
        Test publishing a message calls basic publish on the channel with the configured exchange and
        the string representation of the input json dictionary
        """
        channel_mock = MagicMock()
        connection_mock().channel.return_value = channel_mock
        self.publisher.connect()
        self.publisher.initialize()
        self.publisher(self.TEST_JSON)
        channel_mock.basic_publish.assert_called_with(exchange=self.TEST_EXCHANGE, routing_key='',
                                                      body=json.dumps(self.TEST_JSON))
