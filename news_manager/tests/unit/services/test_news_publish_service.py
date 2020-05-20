"""
News publish service tests module
"""
from unittest import TestCase
from unittest.mock import patch, MagicMock, call

from aiohttp.web_app import Application
from aiounittest import async_test
from news_service_lib.models import New, NamedEntity

from news_manager.services.news_publish_service import NewsPublishService


class TestNewsPublishService(TestCase):
    """
    News publish service test cases implementation
    """
    TEST_RABBIT_CONFIG = dict(test='test')
    TEST_NEW_INSERT_CHANGE = dict(New(title='test_title', content='test_content', date=12313.0, source='test_source',
                                      entities=[
                                          NamedEntity(text='test_named_entity_text', type='test_named_entity_type')]))

    @patch('news_manager.services.news_publish_service.Process')
    @patch('news_manager.services.news_publish_service.ExchangePublisher')
    def setUp(self, publisher_mock, process_mock):
        """
        Initialize the publisher service mocking necessary properties
        """
        self.publisher_mock = publisher_mock
        self.process_mock = process_mock
        self.news_service_mock = MagicMock()
        self.news_service_mock.consume_new_inserts.return_value = [self.TEST_NEW_INSERT_CHANGE,
                                                                   self.TEST_NEW_INSERT_CHANGE]
        self.apm_mock = MagicMock()
        self.app = Application()
        self.app['news_service'] = self.news_service_mock
        self.mocked_config = MagicMock()
        self.mocked_config.get_section.return_value = self.TEST_RABBIT_CONFIG
        self.app['config'] = self.mocked_config
        self.publisher_mock.test_connection.return_value = True
        self.news_publish_service = NewsPublishService(self.app)

    def test_initialize_publisher(self):
        """
        Test initializing publish service creates the exchange publisher in a separate process and runs the process
        """
        self.publisher_mock.assert_called_with(**self.TEST_RABBIT_CONFIG, exchange='news')
        self.process_mock.assert_called_with(target=self.news_publish_service.__call__)
        self.assertTrue(self.process_mock().start.called)

    def test_call_publish_service(self):
        """
        Test calling the publish service initializes the exchange publisher and for each new insertion calls the
        publisher with the new insertion
        """
        self.news_publish_service()
        self.publisher_mock().connect.assert_called_once()
        self.publisher_mock().initialize.assert_called_once()
        self.publisher_mock().assert_called_with(self.TEST_NEW_INSERT_CHANGE)
        call_calls = self.publisher_mock().mock_calls.count(call(self.TEST_NEW_INSERT_CHANGE))
        self.assertEqual(call_calls, 2)

    @async_test
    async def test_shutdown(self):
        """
        Test shutting down the service shutdowns the exchange publisher and waits the consume process
        to join the main thread
        """
        await self.news_publish_service.shutdown()
        self.publisher_mock().shutdown.assert_called_once()
        self.process_mock().join.assert_called_once()
