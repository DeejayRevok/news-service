"""
Exchange consumer unit tests module
"""
from unittest import TestCase
from unittest.mock import MagicMock, patch

from news_manager.infrastructure.messaging.exchange_consumer import ExchangeConsumer


class TestExchangeConsumer(TestCase):
    """
    Exchange consumer test cases implementation
    """
    TEST_HOST = 'test_host'
    TEST_PORT = '0'
    TEST_USER = 'test_user'
    TEST_PASSWORD = 'test_password'
    TEST_EXCHANGE = 'test_exchange'
    TEST_QUEUE_NAME = 'test_queue_name'

    def setUp(self):
        """
        Set up the consumer instance to test
        """
        self.callback = MagicMock()
        self.consumer = ExchangeConsumer(self.TEST_HOST, self.TEST_PORT, self.TEST_USER, self.TEST_PASSWORD,
                                         self.TEST_EXCHANGE, self.TEST_QUEUE_NAME, self.callback)

    @patch('news_manager.infrastructure.messaging.exchange_provider.ConnectionParameters')
    @patch('news_manager.infrastructure.messaging.exchange_provider.PlainCredentials')
    @patch('news_manager.infrastructure.messaging.exchange_provider.BlockingConnection')
    def test_consume(self, ___, _, __):
        """
        Test the consume method creates a channel, declares the exchange and the queue, binds the queue to the exchange
        , defines the consuming from the declared queue and starts consuming
        """
        self.consumer()
        self.assertIsNotNone(self.consumer._channel)
        self.consumer._channel.exchange_declare.assert_called_with(exchange=self.TEST_EXCHANGE, exchange_type='fanout',
                                                                   durable=True)
        self.consumer._channel.queue_declare.assert_called_with(queue=self.TEST_QUEUE_NAME, exclusive=True)
        self.consumer._channel.queue_bind.assert_called_with(exchange=self.TEST_EXCHANGE, queue=self.TEST_QUEUE_NAME)
        self.consumer._channel.basic_consume.assert_called_with(queue=self.TEST_QUEUE_NAME,
                                                                on_message_callback=self.callback,
                                                                auto_ack=True)
        self.consumer._channel.start_consuming.assert_called_once()
