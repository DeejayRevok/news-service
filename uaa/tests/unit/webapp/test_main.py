"""
Application entry point test cases
"""
import unittest
from unittest.mock import patch, MagicMock

from aiohttp.web_app import Application

from uaa.lib.config_tools import parse_config
from uaa.services.users_service import UserService
from uaa.services.authentication_service import AuthService
from uaa.webapp.definitions import CONFIG_PATH
from uaa.webapp.main import init_server


class DummySession:
    pass


class TestMain(unittest.TestCase):

    def test_parse_config(self):
        """
        Test if the parsed configuration contains the minimum required parameters
        """
        config_parsed = parse_config(CONFIG_PATH)
        self.assertIsNotNone(config_parsed.get('server', 'host'))
        self.assertIsNotNone(config_parsed.get('server', 'port'))

    # noinspection PyTypeHints
    @patch('uaa.infrastructure.storage.sql_storage.sessionmaker')
    @patch('uaa.infrastructure.storage.sql_storage.create_engine')
    @patch('uaa.webapp.main.initialize_db')
    @patch('uaa.webapp.main.health_check')
    @patch('uaa.webapp.main.Checker')
    @patch('uaa.webapp.main.ElasticAPM')
    @patch('uaa.webapp.main.Client')
    @patch('uaa.webapp.main.setup_aiohttp_apispec')
    @patch('uaa.webapp.main.users_view')
    @patch('uaa.webapp.main.auth_view')
    def test_init_app(self, auth_view_mock, users_view_mock, apispec_mock, apm_client_mock, apm_middleware_mock
                      , health_checker_mock, _, db_initializer_mock, engine_mock, session_maker_mock):
        """
        Test if the initialization of the app initializes all the required modules
        """
        mock_engine = dict(Engine='engine')
        engine_mock.return_value = mock_engine
        session_maker_mock.return_value = DummySession
        app = init_server()
        apispec_mock.assert_called_once()
        auth_view_mock.setup_routes.assert_called_once()
        users_view_mock.setup_routes.assert_called_once()
        apm_client_mock.assert_called_once()
        health_checker_mock.assert_called_once()
        db_initializer_mock.assert_called_with(mock_engine)
        self.assertTrue(isinstance(apm_middleware_mock.call_args[0][0], Application))
        self.assertTrue(isinstance(apm_middleware_mock.call_args[0][1], MagicMock))
        self.assertIsNotNone(app['user_service'])
        self.assertIsNotNone(app['auth_service'])
        self.assertTrue(isinstance(app['user_service'], UserService))
        self.assertTrue(isinstance(app['auth_service'], AuthService))
        self.assertEqual(app['user_service']._client.engine, mock_engine)
        self.assertEqual(app['auth_service']._user_service, app['user_service'])


if __name__ == '__main__':
    unittest.main()
