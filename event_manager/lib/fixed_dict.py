"""
Fixed dictionary module
"""
import collections
from typing import Iterator, Any


class FixedDict(collections.MutableMapping):
    """
    Dictionary implementation which only allows modifications of the existing value keys
    """
    def __init__(self, data: dict):
        """
        Initialize the fixed dictionary with the specified dictionary data

        Args:
            data: data to fill the fixed dictionary
        """
        self.__data = data

    def __len__(self) -> int:
        """
        Get the dictionary number of keys

        Returns: dictionary length

        """
        return len(self.__data)

    def __iter__(self) -> Iterator[Any]:
        """
        Iterate through the dictionary data

        Returns: iterator to dictionary data

        """
        return iter(self.__data)

    def __setitem__(self, key: str, value: Any):
        """
        Set the specified value to the specified key if the key exists

        Args:
            key: key
            value: value to set

        """
        if key not in self.__data:
            raise KeyError(key)

        self.__data[key] = value

    def __delitem__(self, key: str):
        """
        Avoid key deleting
        """
        raise NotImplementedError

    def __getitem__(self, key: str) -> Any:
        """
        Get the specified key value

        Args:
            key: key to get value

        Returns: value of the key

        """
        return self.__data[key]

    def __contains__(self, key: str) -> bool:
        """
        Check if the dictionary contains the specified key

        Args:
            key: key to check existence

        Returns: True if the key exists, False otherwise

        """
        return key in self.__data
