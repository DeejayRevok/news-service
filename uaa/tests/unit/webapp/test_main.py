"""
Application entry point test cases
"""
import unittest
from unittest.mock import patch

from aiohttp.web_app import Application
from news_service_lib import Configuration

from uaa.infrastructure.storage.sql_storage import SqlStorage
from uaa.services.users_service import UserService
from uaa.services.authentication_service import AuthService
from uaa.webapp.main import init_uaa


class DummySession:
    pass


class TestMain(unittest.TestCase):
    """
    Webapp main test cases implementation
    """
    TEST_STORAGE_CONFIG = dict(host='test', port=0, user='test', password='test', schema='test')

    # noinspection PyTypeHints
    @patch.object(SqlStorage, 'health_check')
    @patch.object(Configuration, 'get_section')
    @patch('uaa.infrastructure.storage.sql_storage.sessionmaker')
    @patch('uaa.infrastructure.storage.sql_storage.create_engine')
    @patch('uaa.webapp.main.initialize_db')
    @patch('uaa.webapp.main.users_view')
    @patch('uaa.webapp.main.auth_view')
    def test_init_app(self, auth_view_mock, users_view_mock, db_initializer_mock, engine_mock, session_maker_mock,
                      config_mock, storage_health_mock):
        """
        Test if the initialization of the app initializes all the required modules
        """
        storage_health_mock.return_value = True
        mock_engine = dict(Engine='engine')
        engine_mock.return_value = mock_engine
        session_maker_mock.return_value = DummySession
        config_mock.get_section.return_value = self.TEST_STORAGE_CONFIG
        base_app = Application()
        base_app['config'] = config_mock
        app = init_uaa(base_app)
        auth_view_mock.setup_routes.assert_called_once()
        users_view_mock.setup_routes.assert_called_once()
        db_initializer_mock.assert_called_with(mock_engine)
        self.assertIsNotNone(app['user_service'])
        self.assertIsNotNone(app['auth_service'])
        self.assertTrue(isinstance(app['user_service'], UserService))
        self.assertTrue(isinstance(app['auth_service'], AuthService))
        self.assertEqual(app['user_service']._client.engine, mock_engine)
        self.assertEqual(app['auth_service']._user_service, app['user_service'])
