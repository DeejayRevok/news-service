"""
Generic source adapter module
"""
from abc import abstractmethod
from typing import Iterator, Any

from news_service_lib.models import New


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

    def fetch(self) -> Iterator[New]:
        """
        Fetch news from the source

        Returns: iterator to source news

        """
        return self.adapt(self._fetch())

    def adapt(self, fetched_items: Iterator[Any]) -> Iterator[New]:
        """
        Convert the fetched news from the source to New instances

        Args:
            fetched_items: items fetched from the source

        Returns: transformed source fetched items

        """
        for item in fetched_items:
            yield self._adapt_single(item)

    @abstractmethod
    def _fetch(self) -> Iterator[Any]:
        """
        Fetch news from the source

        Returns: fetched news

        """

    @abstractmethod
    def _adapt_single(self, item: Any) -> New:
        """
        Convert a single fetched new to New

        Args:
            item: item to convert to New

        Returns: New representation of the item

        """
