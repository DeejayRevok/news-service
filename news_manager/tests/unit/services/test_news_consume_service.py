"""
News consume service tests module
"""
import json
from unittest import TestCase
from unittest.mock import patch, MagicMock

from aiohttp.web_app import Application
from aiounittest import async_test
from news_service_lib.models import New, NamedEntity

from news_manager.services.news_consume_service import NewsConsumeService


class TestNewsConsumeService(TestCase):
    TEST_RABBIT_CONFIG = dict(test='test')
    TEST_NEW = New(title='test_title', content='test_content', date=12313.0, categories=['test_category'],
                   entities=[NamedEntity(text='test_named_entity_text', type='test_named_entity_type')])

    @patch('news_manager.services.news_consume_service.Process')
    @patch('news_manager.services.news_consume_service.ExchangeConsumer')
    def setUp(self, consumer_mock, process_mock):
        """
        Initialize the consumer service mocking necessary properties
        """
        self.consumer_mock = consumer_mock
        self.process_mock = process_mock
        self.news_service_mock = MagicMock()
        self.apm_mock = MagicMock()
        self.app = Application()
        self.app['apm'] = self.apm_mock
        self.app['news_service'] = self.news_service_mock
        self.mocked_config = MagicMock()
        self.mocked_config.get_section.return_value = self.TEST_RABBIT_CONFIG
        self.app['config'] = self.mocked_config
        self.consumer_mock.test_connection.return_value = True
        self.news_consume_service = NewsConsumeService(self.app)

    def test_initialize_consumer(self):
        """
        Test initializing consumer service initializes the exchange consumer in a separate process and runs the process
        """
        self.consumer_mock.assert_called_with(**self.TEST_RABBIT_CONFIG, exchange='news', queue_name='news_updates',
                                              message_callback=self.news_consume_service.new_update)
        self.process_mock.assert_called_with(target=self.consumer_mock().__call__)
        self.assertTrue(self.process_mock().start.called)

    def test_new_update_success(self):
        """
        Test succesful new update creates an apm success transaction and updates the body new
        """
        async def mock_save_new_success():
            """
            Test mocked asynchronous method response
            """
            pass
        self.news_service_mock.save_new.return_value = mock_save_new_success()
        self.news_consume_service.new_update(None, None, None, json.dumps(dict(self.TEST_NEW)))
        self.apm_mock.client.begin_transaction.assert_called_with('consume')
        self.news_service_mock.save_new.assert_called_with(self.TEST_NEW)
        self.apm_mock.client.end_transaction.assert_called_with('New update', 'OK')

    def test_new_update_fail(self):
        """
        Test new update failed creates an apm fail transaction and captures the exception
        """
        self.news_service_mock.save_new.side_effect = Exception('Test')
        self.news_consume_service.new_update(None, None, None, json.dumps(dict(self.TEST_NEW)))
        self.apm_mock.client.end_transaction.assert_called_with('New update', 'FAIL')
        self.apm_mock.client.capture_exception.assert_called_once()

    @async_test
    async def test_shutdown(self):
        """
        Test shutting down the service shutdowns the exchange consumer service and waits the consume process
        to join the main thread
        """
        await self.news_consume_service.shutdown()
        self.consumer_mock().shutdown.assert_called_once()
        self.process_mock().join.assert_called_once()
