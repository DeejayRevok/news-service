import unittest
from unittest.mock import patch, Mock

from news_manager.cron.cron_factory import initialize_crons
from news_manager.infrastructure.storage.mongo_storage import MongoStorage
from news_manager.infrastructure.storage.storage_factory import storage_factory


class DummyImplementation:

    def __init__(self, dummy_app, definition):
        self.app = dummy_app
        self.definition = definition
        dummy_app()


class TestFactories(unittest.TestCase):

    def test_storage_factory_unknown(self):
        """
        Test storage factory raises error for unknown type
        """
        with self.assertRaises(NotImplementedError):
            storage_factory('UNKNOWN', {})

    def test_storage_factory_mongo(self):
        """
        Test storage factory with Mongo type creates Mongo client
        """
        storage = storage_factory('MONGO', {'host': 'test', 'port': 1234, 'database': 'test'})
        self.assertTrue(isinstance(storage, MongoStorage))

    @patch('news_manager.cron.cron_factory.DEFINITIONS')
    def test_initialize_crons(self, mocked_definitions):
        """
        Test the correct initialization of the defined crons
        """
        definitions_dummy = {
            'definition_1': {
                'class': DummyImplementation
            },
            'definition_2': {
                'class': DummyImplementation
            }
        }
        mocked_definitions.values.return_value = definitions_dummy.values()
        mock_app = Mock()
        initialize_crons(mock_app)
        self.assertEqual(mock_app.call_count, 2)


if __name__ == '__main__':
    unittest.main()
