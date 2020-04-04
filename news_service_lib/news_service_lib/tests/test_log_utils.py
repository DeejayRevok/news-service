"""
Log utils tests module
"""
from unittest import TestCase

from ..log_utils import get_base_log_config, add_logstash_handler


class TestServerUtils(TestCase):

    def test_base_log_config(self):
        """
        Test the get log config returns the log config with the required handlers, the required loggers and
        the required formatters
        """
        base_config = get_base_log_config('test')
        self.assertListEqual(['console', 'file'], list(base_config['handlers'].keys()))
        self.assertListEqual(['main_logger'], list(base_config['loggers'].keys()))
        self.assertListEqual(['error', 'debug'], list(base_config['formatters'].keys()))

    def test_add_logstash_handler(self):
        """
        Test the add logstash method adds the logstash handler to the input log config
        """
        base_config = get_base_log_config('test')
        add_logstash_handler(base_config, 'test', 0)
        self.assertIn('logstash', list(base_config['handlers'].keys()))
