import unittest

import mongomock

from infrastructure.storage.filters.storage_filter_type import StorageFilterType
from infrastructure.storage.mongo_storage import MongoStorage
from lib.fixed_dict import FixedDict

mocked_item = {'id': 1, 'test': 'test'}
mocked_item_update = {'id': 1, 'test': 'test2'}


class TestMongoStorage(unittest.TestCase):
    MONGO_HOST = '0.1.2.3'
    MONGO_PORT = 1234
    DATABASE = 'test'
    COLLECTION = 'test'

    @mongomock.patch(servers=((MONGO_HOST, MONGO_PORT),))
    def test_collection_not_set(self):
        mongo_client = MongoStorage(self.MONGO_HOST, self.MONGO_PORT, self.DATABASE)
        with self.assertRaises(AssertionError):
            mongo_client.save(mocked_item)

    @mongomock.patch(servers=((MONGO_HOST, MONGO_PORT),))
    def test_save(self):
        mongo_client = MongoStorage(self.MONGO_HOST, self.MONGO_PORT, self.DATABASE)
        mongo_client.set_collection(self.COLLECTION)
        mongo_client.save(mocked_item)
        stored_item = mongo_client.get_one()
        assert stored_item == mocked_item

    @mongomock.patch(servers=((MONGO_HOST, MONGO_PORT),))
    def test_save_duplicated_update(self):
        mongo_client = MongoStorage(self.MONGO_HOST, self.MONGO_PORT, self.DATABASE)
        mongo_client.set_collection(self.COLLECTION)
        mongo_client.save(mocked_item)
        mongo_client.save(mocked_item_update, exist_filter=StorageFilterType.UNIQUE,
                          exist_params=FixedDict(dict(key='id', value=1)))
        stored_items = list(mongo_client.get())
        del mocked_item_update['_id']
        assert len(stored_items) == 1
        assert stored_items[0] == mocked_item_update


if __name__ == '__main__':
    unittest.main()
