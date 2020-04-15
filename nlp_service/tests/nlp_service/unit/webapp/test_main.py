"""
Main nlp webapp module tests
"""
import unittest
from unittest.mock import patch

from aiohttp.web_app import Application
from aiohttp_apispec import validation_middleware
from news_service_lib import uaa_auth_middleware
from news_service_lib.config import Configuration

from nlp_service.webapp.main import init_nlp_service
from nlp_service.webapp.middlewares import error_middleware


class TestMain(unittest.TestCase):

    TEST_CONFIG = dict(protocol='test', host='test', port=0)

    # noinspection PyTypeHints
    @patch('nlp_service.webapp.main.initialize_worker')
    @patch('nlp_service.webapp.main.CELERY_APP')
    @patch('nlp_service.webapp.main.NlpService')
    @patch.object(Configuration, 'get')
    @patch('nlp_service.webapp.main.health_check')
    @patch('nlp_service.webapp.main.nlp_view')
    def test_init_app(self, view_mock, _, config_mock, __, celery_app_mock, init_worker_task_mock):
        """
        Test if the initialization of the app initializes all the required services, adds the required middlewares,
        setups the required routes, configures the celery app and initializes all the celery worker subprocesses
        """
        config_mock.get_section.return_value = self.TEST_CONFIG
        config_mock.get.return_value = 3
        base_app = Application()
        base_app['config'] = config_mock
        app = init_nlp_service(base_app)
        view_mock.setup_routes.assert_called_once()
        celery_app_mock.configure.assert_called_once()
        self.assertEqual(len(init_worker_task_mock.mock_calls), 3)
        self.assertIsNotNone(app['nlp_service'])
        self.assertIsNotNone(app['uaa_service'])
        self.assertIn(error_middleware, app.middlewares)
        self.assertIn(uaa_auth_middleware, app.middlewares)
        self.assertIn(validation_middleware, app.middlewares)


if __name__ == '__main__':
    unittest.main()
