"""
MongoDB storage implementation module
"""
import functools
from typing import Callable, Any, Iterator, List

import pymongo

from infrastructure.storage.filters.mongo_filter import MongoFilter
from infrastructure.storage.filters.storage_filter_type import StorageFilterType
from infrastructure.storage.storage import Storage
from lib.fixed_dict import FixedDict
from log_config import get_logger

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
        assert args[0].collection is not None, 'Collection not set'

        return function(*args, **kwargs)
    return managed


class MongoStorage(Storage):
    """
    MongoDB storage implementation
    """
    def __init__(self, host: str, port: int, database: str):
        """
        Initialize a mongo storage client

        Args:
            host: mongodb host address
            port: mongodb port
            database: mongodb database name
        """
        mongo_client = pymongo.MongoClient(host, int(port), connect=True)
        self._database = mongo_client[database]
        self.collection = None

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
    def get(self, filter_types: List[StorageFilterType] = None, filters_params: List[FixedDict] = None) -> Iterator[dict]:
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
