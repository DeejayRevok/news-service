import unittest

import mongomock

from infrastructure.storage.filters.storage_filter_type import StorageFilterType
from infrastructure.storage.mongo_storage import MongoStorage
from lib.fixed_dict import FixedDict

MOCKED_ITEM = {'id': 1, 'test': 'test'}
MOCKED_ITEM_UPDATE = {'id': 1, 'test': 'test2'}


class TestMongoStorage(unittest.TestCase):
    MONGO_HOST = '0.1.2.3'
    MONGO_PORT = 1234
    DATABASE = 'test'
    COLLECTION = 'test'

    @mongomock.patch(servers=((MONGO_HOST, MONGO_PORT),))
    def test_collection_not_set(self):
        mongo_client = MongoStorage(self.MONGO_HOST, self.MONGO_PORT, self.DATABASE)
        with self.assertRaises(AssertionError):
            mongo_client.save(MOCKED_ITEM)

    @mongomock.patch(servers=((MONGO_HOST, MONGO_PORT),))
    def test_save(self):
        mongo_client = MongoStorage(self.MONGO_HOST, self.MONGO_PORT, self.DATABASE)
        mongo_client.set_collection(self.COLLECTION)
        mongo_client.save(MOCKED_ITEM)
        stored_item = mongo_client.get_one()
        assert stored_item == MOCKED_ITEM

    @mongomock.patch(servers=((MONGO_HOST, MONGO_PORT),))
    def test_save_duplicated_update(self):
        mongo_client = MongoStorage(self.MONGO_HOST, self.MONGO_PORT, self.DATABASE)
        mongo_client.set_collection(self.COLLECTION)
        mongo_client.save(MOCKED_ITEM)
        mongo_client.save(MOCKED_ITEM_UPDATE, exist_filter=StorageFilterType.UNIQUE,
                          exist_params=FixedDict(dict(key='id', value=1)))
        stored_items = list(mongo_client.get())
        del MOCKED_ITEM_UPDATE['_id']
        assert len(stored_items) == 1
        assert stored_items[0] == MOCKED_ITEM_UPDATE

    @mongomock.patch(servers=((MONGO_HOST, MONGO_PORT),))
    def test_get_one(self):
        mongo_client = MongoStorage(self.MONGO_HOST, self.MONGO_PORT, self.DATABASE)
        mongo_client.set_collection(self.COLLECTION)
        mongo_client.save(MOCKED_ITEM)
        mongo_client.save(MOCKED_ITEM_UPDATE)

        first_item = mongo_client.get_one()
        assert first_item == MOCKED_ITEM

        query_item = mongo_client.get_one({'test': 'test2'})
        assert query_item == MOCKED_ITEM_UPDATE

    @mongomock.patch(servers=((MONGO_HOST, MONGO_PORT),))
    def test_get(self):
        mongo_client = MongoStorage(self.MONGO_HOST, self.MONGO_PORT, self.DATABASE)
        mongo_client.set_collection(self.COLLECTION)
        mongo_client.save(MOCKED_ITEM)
        mongo_client.save(MOCKED_ITEM_UPDATE)

        items = mongo_client.get()
        assert list(items) == [MongoStorage.render_item(MOCKED_ITEM), MongoStorage.render_item(MOCKED_ITEM_UPDATE)]

        filtered_items = list(mongo_client.get(filter_types=[StorageFilterType.UNIQUE],
                                               filters_params=[FixedDict(dict(key='test', value='test2'))]))
        assert len(filtered_items) == 1
        assert filtered_items[0] == MOCKED_ITEM_UPDATE

    @mongomock.patch(servers=((MONGO_HOST, MONGO_PORT),))
    def test_delete(self):
        mongo_client = MongoStorage(self.MONGO_HOST, self.MONGO_PORT, self.DATABASE)
        mongo_client.set_collection(self.COLLECTION)
        mongo_client.save(MOCKED_ITEM)

        items = list(mongo_client.get())
        assert len(items) == 1

        mongo_client.delete(MOCKED_ITEM['_id'])
        items = list(mongo_client.get())
        assert len(items) == 0


if __name__ == '__main__':
    unittest.main()
