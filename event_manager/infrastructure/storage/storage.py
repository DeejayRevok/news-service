"""
Abstract storage module
"""
from abc import ABCMeta, abstractmethod
from typing import Iterator, List

from event_manager.infrastructure.storage.filters.storage_filter_type import StorageFilterType
from event_manager.lib.fixed_dict import FixedDict


class Storage(metaclass=ABCMeta):
    """
    Storage interface
    """

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the storage is available

        Returns: True if the storage is available, False otherwise

        """

    @abstractmethod
    def save(self, item: dict, exist_filter: StorageFilterType = None, exist_params: FixedDict = None):
        """
        Persist the specified item if specified filters do not match

        Args:
            item: item to persist
            exist_filter: type of filter to check item existence
            exist_params: existence filter parameters

        """

    @abstractmethod
    def get(self, filter_types: List[StorageFilterType] = None, filters_params: List[FixedDict] = None) -> Iterator[dict]:
        """
        Get items from the storage. If filters are provided filter results.

        Args:
            filter_types: type of the filters to apply
            filters_params: filters params

        Returns: iterator to dictionary representation of the items

        """

    @abstractmethod
    def get_one(self, query: dict = None) -> dict:
        """
        Get the first storage item. If query is specified apply it.

        Args:
            query: query for the storage

        Returns: persisted item

        """

    @abstractmethod
    def delete(self, identifier: str):
        """
        Delete the specified stored item

        Args:
            identifier: identifier of the item to delete

        """
