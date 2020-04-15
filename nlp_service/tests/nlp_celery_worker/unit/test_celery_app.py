"""
Main celery app unit tests module
"""
import sys
from unittest import TestCase
from unittest.mock import patch

from nlp_service.nlp_celery_worker.celery_app import CeleryApp


class TestCeleryApp(TestCase):
    TEST_BROKER_CONFIG = {
        'host': 'test_host',
        'port': '0',
        'user': 'test_user',
        'password': 'test_password'
    }
    TEST_CONCURRENCY = 1

    @patch('nlp_service.nlp_celery_worker.celery_app.Celery')
    def setUp(self, _):
        """
        Setup the test variables
        """
        self.celery_app = CeleryApp()

    def test_configure(self):
        """
        Test the configure method sets the broker url with the correct format,
        the result backend and the worker concurrency
        """
        self.celery_app.configure(self.TEST_BROKER_CONFIG, self.TEST_CONCURRENCY)
        self.celery_app.app.config_from_object.assert_called_with(dict(
            broker_url=f'pyamqp://{self.TEST_BROKER_CONFIG["user"]}:{self.TEST_BROKER_CONFIG["password"]}'
                       f'@{self.TEST_BROKER_CONFIG["host"]}:{self.TEST_BROKER_CONFIG["port"]}//',
            result_backend='rpc://',
            worker_concurrency=self.TEST_CONCURRENCY))

    def test_run(self):
        """
        Test the run method resets the system argument and starts the celery worker
        """
        self.celery_app.run()
        self.assertEqual(len(sys.argv), 1)
        self.celery_app.app.worker_main.assert_called_once()
