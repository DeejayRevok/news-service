import unittest
from unittest.mock import patch, MagicMock

from aiohttp.web_app import Application

from lib.sources.config_tools import parse_config
from event_manager.services.event_service import EventService
from event_manager.webapp.definitions import CONFIG_PATH
from event_manager.webapp.main import init_app


class TestMain(unittest.TestCase):

    def test_parse_config(self):
        """
        Test if the parsed configuration contains the minimum required parameters
        """
        config_parsed = parse_config(CONFIG_PATH)
        self.assertIsNotNone(config_parsed.get('server', 'host'))
        self.assertIsNotNone(config_parsed.get('server', 'port'))
        self.assertIsNotNone(config_parsed.get('server', 'storage'))

    # noinspection PyTypeHints
    @patch('event_manager.webapp.main.health_check')
    @patch('event_manager.webapp.main.Checker')
    @patch('event_manager.webapp.main.ElasticAPM')
    @patch('event_manager.webapp.main.Client')
    @patch('event_manager.webapp.main.initialize_crons')
    @patch('event_manager.webapp.main.setup_aiohttp_apispec')
    @patch('event_manager.webapp.main.events_view')
    @patch('event_manager.webapp.main.storage_factory')
    def test_init_app(self, storage_factory_mock, view_mock, apispec_mock, init_crons_mock, apm_client_mock,
                      apm_middleware_mock, health_checker_mock, _):
        """
        Test if the initialization of the app initializes all the required modules
        """
        test_storage_client = dict(test='test')
        storage_factory_mock.return_value = test_storage_client
        app = init_app()
        self.assertEqual(init_crons_mock.call_args[0][0], app)
        apispec_mock.assert_called_once()
        view_mock.setup_routes.assert_called_once()
        apm_client_mock.assert_called_once()
        health_checker_mock.assert_called_once()
        self.assertTrue(isinstance(apm_middleware_mock.call_args[0][0], Application))
        self.assertTrue(isinstance(apm_middleware_mock.call_args[0][1], MagicMock))
        self.assertIsNotNone(app['event_service'])
        self.assertTrue(isinstance(app['event_service'], EventService))
        self.assertEqual(app['event_service']._client, test_storage_client)


if __name__ == '__main__':
    unittest.main()
