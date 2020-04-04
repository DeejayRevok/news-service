"""
News service module
"""
from typing import Iterator

from news_manager.infrastructure.storage.filters.storage_filter_type import StorageFilterType
from news_manager.infrastructure.storage.models.new import New
from news_manager.infrastructure.storage.mongo_storage import MongoStorage
from news_manager.infrastructure.storage.storage import Storage


class NewsService:
    """
    Class used to manage the interaction with the news
    """

    def __init__(self, client: Storage):
        """
        Initialize the NEWS service with the specified storage client

        Args:
            client: storage client
        """
        self._client = client
        if isinstance(self._client, MongoStorage):
            self._client.set_collection('new')

    async def save_new(self, new: New):
        """
        Persist the specified new

        Args:
            new: new to persist

        """
        exist_filter_params = StorageFilterType.UNIQUE.params
        exist_filter_params['key'] = 'title'
        exist_filter_params['value'] = new.title
        self._client.save(dict(new), exist_filter=StorageFilterType.UNIQUE, exist_params=exist_filter_params)

    async def get_news(self, start: int = None, end: int = None) -> Iterator[New]:
        """
        Get news with date within the specified time range

        Args:
            start: start date timestamp of the filter range
            end: end date timestamp of the filter range

        Returns: iterator to the filtered news

        """
        filter_types = []
        filters_params = []
        if start is not None or end is not None:
            range_filter_params = StorageFilterType.RANGE.params
            range_filter_params['key'] = 'date'
            range_filter_params['upper'] = end
            range_filter_params['lower'] = start

            filter_types.append(StorageFilterType.RANGE)
            filters_params.append(range_filter_params)

        return NewsService._render_news_list(self._client.get(filter_types, filters_params))

    @staticmethod
    def _render_news_list(news_list: Iterator[dict]) -> Iterator[New]:
        """
        Render the news from the specified list

        Args:
            news_list: news to render

        Returns: iterator to the rendered news

        """
        for new in news_list:
            yield NewsService._render_new(new)

    @staticmethod
    def _render_new(new: dict) -> New:
        """
        Render a single new

        Args:
            new: new to render

        Returns: rendered new

        """
        return New(**new)
