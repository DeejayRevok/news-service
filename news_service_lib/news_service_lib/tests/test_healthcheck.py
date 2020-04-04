"""
Healthcheck tests module
"""
from unittest import TestCase
from unittest.mock import patch, MagicMock

from aiohttp.web_app import Application
from aiounittest import async_test

from ..healthcheck import HealthCheck


class TestHealthCheck(TestCase):

    @patch('news_service_lib.healthcheck.Checker')
    @async_test
    async def test_healthcheck(self, checker_mock):
        """
        Test the healthcheck calls the specified healthchecker for the input app
        """
        checker_function_mock = MagicMock()

        async def checker_function_async(_):
            checker_function_mock()

        app = Application()
        healthchecker = HealthCheck(app, checker_function_async)
        self.assertTrue(checker_mock.called)
        await healthchecker.health_check()
        checker_function_mock.assert_called_once()
