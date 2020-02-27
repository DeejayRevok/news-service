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

    def __setitem__(self, k: str, v: Any):
        """
        Set the specified value to the specified key if the key exists

        Args:
            k: key
            v: value to set

        """
        if k not in self.__data:
            raise KeyError(k)

        self.__data[k] = v

    def __delitem__(self, k: str):
        """
        Avoid key deleting
        """
        raise NotImplementedError

    def __getitem__(self, k: str) -> Any:
        """
        Get the specified key value

        Args:
            k: key to get value

        Returns: value of the key

        """
        return self.__data[k]

    def __contains__(self, k: str) -> bool:
        """
        Check if the dictionary contains the specified key

        Args:
            k: key to check existence

        Returns: True if the key exists, False otherwise

        """
        return k in self.__data
