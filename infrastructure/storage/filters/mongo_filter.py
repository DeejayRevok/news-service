"""
MongoDB filter module
"""
from infrastructure.storage.filters.filter import StorageFilter
from lib.fixed_dict import FixedDict


class MongoFilter(StorageFilter):
    """
    MongoDB filter implementation
    """
    @staticmethod
    def parse_unique(params: FixedDict) -> dict:
        """
        Get the unique filter query with the specified parameters

        Args:
            params: unique filter parameters

        Returns: mongodb query

        """
        return {params['key']: params['value']}

    @staticmethod
    def parse_range(params: FixedDict) -> dict:
        """
        Get the range filter query with the specified parameters

        Args:
            params: range filter parameters

        Returns: mongodb query

        """
        key_query = {}
        if 'lower' in params and params['lower'] is not None:
            key_query['$gt'] = params['lower']
        if 'upper' in params and params['upper'] is not None:
            key_query['$lt'] = params['upper']
        return {params['key']: key_query}
