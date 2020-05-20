"""
Exchange provider tests module
"""
from unittest import TestCase
from unittest.mock import patch, MagicMock

from pika.exceptions import AMQPConnectionError

from news_manager.infrastructure.messaging.exchange_provider import ExchangeProvider


class TestExchangeProvider(TestCase):
    """
    Exchange provider test cases implementation
    """
    TEST_HOST = 'test_host'
    TEST_PORT = '0'
    TEST_USER = 'test_user'
    TEST_PASSWORD = 'test_password'
    TEST_EXCHANGE = 'test_exchange'

    def setUp(self):
        """
        Set up the provider instance to test
        """
        self.provider = ExchangeProvider(self.TEST_HOST, self.TEST_PORT, self.TEST_USER, self.TEST_PASSWORD,
                                         self.TEST_EXCHANGE)

    @patch('news_manager.infrastructure.messaging.exchange_provider.ConnectionParameters')
    @patch('news_manager.infrastructure.messaging.exchange_provider.PlainCredentials')
    @patch('news_manager.infrastructure.messaging.exchange_provider.BlockingConnection')
    def test_test_connection_success(self, mock_connection, mock_credentials, mock_parameters):
        """
        Test the test connection successful creates the connection with the instance parameters and credentials
        """
        result = self.provider.test_connection()
        self.assertTrue(result)
        mock_credentials.assert_called_with(self.TEST_USER, self.TEST_PASSWORD)
        mock_parameters.assert_called_with(host=self.TEST_HOST, port=int(self.TEST_PORT),
                                           credentials=mock_credentials())
        mock_connection.assert_called_with(mock_parameters())

    @patch('news_manager.infrastructure.messaging.exchange_provider.ConnectionParameters')
    @patch('news_manager.infrastructure.messaging.exchange_provider.PlainCredentials')
    @patch('news_manager.infrastructure.messaging.exchange_provider.BlockingConnection')
    def test_test_connection_fail(self, mock_connection, _, __):
        """
        Test the test connection fail returns false when ampq connection error is raised
        """
        mock_connection.side_effect = AMQPConnectionError()
        result = self.provider.test_connection()
        self.assertFalse(result)

    @patch('news_manager.infrastructure.messaging.exchange_provider.ConnectionParameters')
    @patch('news_manager.infrastructure.messaging.exchange_provider.PlainCredentials')
    @patch('news_manager.infrastructure.messaging.exchange_provider.BlockingConnection')
    def test_shutdown(self, mock_connection, _, __):
        """
        Test shutting down the exchange provider closes the channel and the connection
        """
        channel_mock = MagicMock()
        mock_connection().channel.return_value = channel_mock
        self.provider.connect()
        self.provider.initialize()
        self.provider.shutdown()
        mock_connection().close.assert_called_once()
        channel_mock.close.assert_called_once()
