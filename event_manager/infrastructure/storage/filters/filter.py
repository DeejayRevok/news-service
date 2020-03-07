"""
Abstract storage filter module
"""
from abc import abstractmethod, ABCMeta

from event_manager.lib.fixed_dict import FixedDict


class StorageFilter(metaclass=ABCMeta):
    """
    Abstract storage filter interface
    """
    @staticmethod
    @abstractmethod
    def parse_range(params: FixedDict) -> dict:
        """
        Parse the range filter parameters

        Args:
            params: parameters to parse

        Returns: parsed parameters

        """
        pass

    @staticmethod
    @abstractmethod
    def parse_unique(params: FixedDict) -> dict:
        """
        Parse the unique filter parameters

        Args:
            params: parameters to parse

        Returns: parsed parameters

        """
        pass
