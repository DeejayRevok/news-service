"""
Test for the definitions module functions
"""
import unittest
from unittest.mock import patch

from aiounittest import async_test

from uaa.webapp.definitions import health_check


class MockConfig:
    """
    Mocked configuration for the healthcheck test
    """
    def __init__(self):
        self._sections = dict(storage=dict(test='test_storage'))


class TestDefinitions(unittest.TestCase):
    """
    Test case for definitions module
    """
    @patch('uaa.webapp.definitions.SqlStorage')
    @patch('uaa.webapp.definitions.parse_config')
    @async_test
    async def test_healthcheck(self, config_parse_mock, sql_storage_mock):
        """
        Test the app healthcheck method
        """
        config_parse_mock.return_value = MockConfig()
        sql_storage_mock.health_check.return_value = True
        health = await health_check()
        self.assertTrue(health)
        sql_storage_mock.assert_called_with(test='test_storage')
