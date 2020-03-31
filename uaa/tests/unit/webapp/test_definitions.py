"""
Test for the definitions module functions
"""
import unittest
from unittest.mock import patch

from aiohttp.web_app import Application
from aiounittest import async_test

from lib.sources.config import Configuration
from uaa.webapp.definitions import health_check


class TestDefinitions(unittest.TestCase):
    """
    Test case for definitions module
    """
    TEST_STORAGE_CONFIG = dict(host='test', port=0, user='test', password='test', schema='test')

    @patch.object(Configuration, 'get_section')
    @patch('uaa.webapp.definitions.SqlStorage')
    @async_test
    async def test_healthcheck(self, sql_storage_mock, config_mock):
        """
        Test the app healthcheck method
        """
        config_mock.get_section.return_value = self.TEST_STORAGE_CONFIG
        app = Application()
        app['config'] = config_mock
        sql_storage_mock.health_check.return_value = True
        health = await health_check(app)
        self.assertTrue(health)
        sql_storage_mock.assert_called_with(**self.TEST_STORAGE_CONFIG)
