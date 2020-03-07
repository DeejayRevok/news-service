"""
Storage type filter module
"""
from enum import Enum
from typing import Callable

from event_manager.lib.fixed_dict import FixedDict


class StorageFilterType(Enum):
    """
    Storage filter types:
        UNIQUE: filter items which match with one value
        RANGE: filter items which match the specified range
    """
    UNIQUE = ('parse_unique', FixedDict(dict(key=None, value=None)))
    RANGE = ('parse_range', FixedDict(dict(key=None, upper=None, lower=None)))

    @property
    def params(self) -> FixedDict:
        """
        Get the storage filter type required parameters

        Returns: storage filter required parameters

        """
        return self.value[1]

    def get_filter_implementation(self, cls) -> Callable:
        """
        Get the specific filter parsing function

        Args:
            cls: class to search for the parsing function

        Returns: filter parsing function

        """
        return getattr(cls, self.value[0])
