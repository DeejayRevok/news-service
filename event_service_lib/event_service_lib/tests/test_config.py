from unittest import TestCase
from unittest.mock import patch, MagicMock

from ..config import Configuration, ConfigProfile


class TestConfig(TestCase):

    @patch('event_service_lib.config.configparser')
    def test_get(self, configparser_mock):
        test_return_value = 'test'
        raw_mock = MagicMock()
        configparser_mock.RawConfigParser.return_value = raw_mock
        config = Configuration(ConfigProfile.LOCAL, 'test')
        raw_mock.get.return_value = test_return_value
        self.assertEqual(test_return_value, config.get('test', 'test'))

    @patch('event_service_lib.config.configparser')
    def test_get_section(self, configparser_mock):
        test_section = {'test': 'test'}
        raw_mock = MagicMock()
        configparser_mock.RawConfigParser.return_value = raw_mock
        config = Configuration(ConfigProfile.LOCAL, 'test')
        raw_mock._sections = {'test_section': test_section}
        self.assertEqual(test_section, config.get_section('test_section'))
