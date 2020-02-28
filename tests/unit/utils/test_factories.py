import unittest


from infrastructure.storage.mongo_storage import MongoStorage
from infrastructure.storage.storage_factory import storage_factory


class TestFactories(unittest.TestCase):

    def test_storage_factory_unknown(self):
        """
        Test storage factory raises error for unknown type
        """
        with self.assertRaises(AssertionError):
            storage_factory('UNKNOWN', {})

    def test_storage_factory_mongo(self):
        """
        Test storage factory with Mongo type creates Mongo client
        """
        storage = storage_factory('MONGO', {'host': 'test', 'port': 1234, 'database': 'test'})
        assert isinstance(storage, MongoStorage)


if __name__ == '__main__':
    unittest.main()
