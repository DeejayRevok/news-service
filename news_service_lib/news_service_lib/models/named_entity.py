"""
Named entity module
"""
from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class NamedEntity:
    """
    Named entity model class
    """
    text: str
    type: str

    def __iter__(self) -> iter:
        """
        Get an iterator to the named entity properties

        Returns: iterator to named entity properties

        """
        yield 'text', self.text
        yield 'type', self.type
