"""
Storage type filter module
"""
from enum import Enum
from typing import Callable

from news_manager.lib.fixed_dict import FixedDict


class StorageFilterType(Enum):
    """
    Storage filter types:
        UNIQUE: filter items which match with one value
        RANGE: filter items which match the specified range
    """
    UNIQUE = ('parse_unique', ['key', 'value'])
    RANGE = ('parse_range', ['key', 'upper', 'lower'])

    @property
    def params(self) -> FixedDict:
        """
        Get the storage filter type required parameters

        Returns: storage filter required parameters

        """
        return FixedDict(dict.fromkeys(self.value[1], None))

    def get_filter_implementation(self, cls) -> Callable:
        """
        Get the specific filter parsing function

        Args:
            cls: class to search for the parsing function

        Returns: filter parsing function

        """
        return getattr(cls, self.value[0])
