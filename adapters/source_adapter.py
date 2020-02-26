"""
Generic source adapter module
"""
from abc import abstractmethod
from typing import Iterator, Any


class SourceAdapter:
    """
    Generic source adapter interface
    """

    def __init__(self, source_params: dict):
        """
        Initialize the generic source adapter with the specified usage params

        Args:
            source_params: source usage params
        """
        self.source_params = source_params

    def fetch(self) -> Iterator[dict]:
        """
        Fetch items from the source

        Returns: iterator to source items

        """
        return self.adapt(self._fetch())

    def adapt(self, fetched_items: Iterator[Any]) -> Iterator[dict]:
        """
        Convert the fetched items from the source to dictionary

        Args:
            fetched_items: items fetched from the source

        Returns: transformed source fetched items

        """
        for item in fetched_items:
            yield self._adapt_single(item)

    @abstractmethod
    def _fetch(self) -> Iterator[Any]:
        """
        Fetch items from the source

        Returns: fetched items

        """
        pass

    @abstractmethod
    def _adapt_single(self, item: Any) -> dict:
        """
        Convert a single fetched item to dict

        Args:
            item: item to convert to dict

        Returns: dictionary representation of the item

        """
        pass
