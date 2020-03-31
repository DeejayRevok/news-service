import unittest
from unittest.mock import patch

from aiohttp.web_app import Application
from event_service_lib.config import Configuration

from event_manager.services.event_service import EventService
from event_manager.services.uaa_service import UaaService
from event_manager.webapp.main import init_event_manager


class TestMain(unittest.TestCase):

    TEST_CONFIG = dict(protocol='test', host='test', port=0)

    # noinspection PyTypeHints
    @patch.object(Configuration, 'get')
    @patch('event_manager.webapp.main.health_check')
    @patch('event_manager.webapp.main.initialize_crons')
    @patch('event_manager.webapp.main.events_view')
    @patch('event_manager.webapp.main.storage_factory')
    def test_init_app(self, storage_factory_mock, view_mock, init_crons_mock, _, config_mock):
        """
        Test if the initialization of the app initializes all the required modules
        """
        test_storage_client = dict(test='test')
        storage_factory_mock.return_value = test_storage_client
        config_mock.get_section.return_value = self.TEST_CONFIG
        config_mock.get.return_value = 'test'
        base_app = Application()
        base_app['config'] = config_mock
        app = init_event_manager(base_app)
        self.assertEqual(init_crons_mock.call_args[0][0], app)
        view_mock.setup_routes.assert_called_once()
        self.assertIsNotNone(app['event_service'])
        self.assertIsNotNone(app['uaa_service'])
        self.assertTrue(isinstance(app['event_service'], EventService))
        self.assertTrue(isinstance(app['uaa_service'], UaaService))
        self.assertEqual(app['event_service']._client, test_storage_client)


if __name__ == '__main__':
    unittest.main()
