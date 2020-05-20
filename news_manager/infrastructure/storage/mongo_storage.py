"""
MongoDB storage implementation module
"""
import functools
from typing import Callable, Any, Iterator, List

import pymongo
from pymongo.errors import ServerSelectionTimeoutError

from news_manager.infrastructure.storage.filters.mongo_filter import MongoFilter
from news_manager.infrastructure.storage.filters.storage_filter_type import StorageFilterType
from news_manager.infrastructure.storage.storage import Storage
from news_manager.lib.fixed_dict import FixedDict
from news_manager.log_config import get_logger

LOGGER = get_logger()


def check_collection(function: Callable) -> Any:
    """
    Check if collection is configured

    Args:
        function: check before this function execution

    Returns: fn execution result

    """

    @functools.wraps(function)
    def managed(*args, **kwargs) -> Any:
        """
        Decorate the decorated function with its input args and kwargs

        Args:
            *args: decorated function execution positional arguments
            **kwargs: decorated function execution keyword arguments

        Returns: decorated function execution result

        """
        if args[0].collection is not None:
            return function(*args, **kwargs)
        else:
            raise AttributeError('Collection not set')

    return managed


class MongoStorage(Storage):
    """
    MongoDB storage implementation
    """

    def __init__(self, members: str, rsname: str, database: str):
        """
        Initialize a mongo storage client

        Args:
            members: mongodb replicaset members address
            rsname: mongodb replicaset name
            database: mongodb database name
        """
        members = members.split(',')
        self._init_replicaset(members, rsname)
        self._mongo_client = pymongo.MongoClient(members[0], replicaset=rsname, connect=True)
        self._database = self._mongo_client[database]
        self.collection = None

    @staticmethod
    def _init_replicaset(members: List[str], rsname: str):
        """
        Initialize the mongodb replicaset

        Args:
            members: replicaset members addresses
            rsname: replicaset name

        """
        try:
            first_host = members[0].split(':')[0]
            first_port = int(members[0].split(':')[1])
            mongo_admin_client = pymongo.MongoClient(first_host, first_port, connect=True)
            rs_config = {'_id': rsname, 'members': [{'_id': 0, 'host': members[0]}, {'_id': 1, 'host': members[1]}]}
            mongo_admin_client.admin.command("replSetInitiate", rs_config)
            mongo_admin_client.close()
        except Exception as ex:
            LOGGER.info('Replicaset already initialized %s', str(ex))

    def health_check(self) -> bool:
        """
        Check if the mongodb storage is available

        Returns: True if mongodb is available, False otherwise

        """
        try:
            self._mongo_client.server_info()
            return True
        except ServerSelectionTimeoutError:
            LOGGER.error('MongoDB is not available at %s', self._mongo_client.HOST + self._mongo_client.PORT)
            return False

    def set_collection(self, collection: str):
        """
        Set collection used by the implementation

        Args:
            collection: collection to use

        """
        self.collection = self._database[collection]

    @check_collection
    def save(self, item: dict, exist_filter: StorageFilterType = None, exist_params: FixedDict = None):
        """
        Persist the specified item if filters do not match

        Args:
            item: item to persist
            exist_filter: type of the filter to check existence
            exist_params: existence filter parameters

        """
        if exist_filter is not None:
            filter_parser = exist_filter.get_filter_implementation(MongoFilter)
            query = filter_parser(exist_params)
            existing_item = self.get_one(query)
            if existing_item is not None:
                self.delete(existing_item['_id'])
        self.collection.insert_one(item)

    @check_collection
    def get(self, filter_types: List[StorageFilterType] = None, filters_params: List[FixedDict] = None) \
            -> Iterator[dict]:
        """
        Get items which match the specified filters

        Args:
            filter_types: types of the filters to apply
            filters_params: filters parameters

        Returns: iterator to the matching items

        """
        if filter_types is not None and len(filter_types) > 0:
            aggregated_query = {}
            for i, filter_type in enumerate(filter_types):
                filter_parser = filter_type.get_filter_implementation(MongoFilter)
                query = filter_parser(filters_params[i])
                aggregated_query = {**aggregated_query, **query}
            cursor = self.collection.find(aggregated_query)
        else:
            cursor = self.collection.find()

        for item in cursor:
            yield MongoStorage.render_item(item)

    @check_collection
    def get_one(self, query: dict = None) -> dict:
        """
        Get first queried item

        Args:
            query: query to apply

        Returns: first query matching item

        """
        return self.collection.find_one(query)

    @check_collection
    def delete(self, identifier: str):
        """
        Delete the identified item

        Args:
            identifier: identifier of the item

        """
        self.collection.remove(identifier)

    @check_collection
    def consume_inserts(self) -> Iterator[dict]:
        """
        Consume the insert operations

        """
        insert_consumer = self.collection.watch([{'$match': {'operationType': 'insert'}}])
        try:
            for insert_change in insert_consumer:
                yield self.render_item(insert_change['fullDocument'])
        except Exception as ex:
            insert_consumer.close()
            raise ex
        except KeyboardInterrupt as kex:
            insert_consumer.close()
            raise kex

    @staticmethod
    def render_item(item: dict) -> dict:
        """
        Remove additional mongodb data from the item

        Args:
            item: item to clean

        Returns: cleaned item

        """
        del item['_id']
        return item
