import unittest
from unittest.mock import patch

from services.event_service import EventService
from webapp.main import parse_config, init_app


class TestMain(unittest.TestCase):

    def test_parse_config(self):
        """
        Test if the parsed configuration contains the minimum required parameters
        """
        config_parsed = parse_config()
        self.assertIsNotNone(config_parsed.get('server', 'host'))
        self.assertIsNotNone(config_parsed.get('server', 'port'))
        self.assertIsNotNone(config_parsed.get('server', 'storage'))

    @patch('webapp.main.initialize_crons')
    @patch('webapp.main.setup_aiohttp_apispec')
    @patch('webapp.main.events_view')
    @patch('webapp.main.storage_factory')
    def test_init_app(self, storage_factory_mock, view_mock, apispec_mock, init_crons_mock):
        """
        Test if the initialization of the app initializes all the required modules
        """
        test_storage_client = dict(test='test')
        storage_factory_mock.return_value = test_storage_client
        app = init_app()
        self.assertEqual(init_crons_mock.call_args[0][0], app)
        apispec_mock.assert_called_once()
        view_mock.setup_routes.assert_called_once()
        self.assertIsNotNone(app['event_service'])
        self.assertTrue(isinstance(app['event_service'], EventService))
        self.assertEqual(app['event_service']._client, test_storage_client)


if __name__ == '__main__':
    unittest.main()
