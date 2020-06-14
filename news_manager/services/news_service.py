"""
News service module
"""
from typing import Iterator, Tuple

from news_service_lib.models import New

from news_manager.infrastructure.storage.filters.storage_filter_type import StorageFilterType
from news_manager.infrastructure.storage.mongo_storage import MongoStorage
from news_manager.infrastructure.storage.storage import Storage
from news_manager.lib.fixed_dict import FixedDict


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

    async def get_new_by_title(self, title: str) -> New:
        """
        Get an stored new looking for it by title

        Args:
            title: title of the new to search for

        Returns: found new with the specified title

        """
        unique_filter_params = StorageFilterType.UNIQUE.params
        unique_filter_params['key'] = 'title'
        unique_filter_params['value'] = title

        found_new = next(self._client.get(filter_types=[StorageFilterType.UNIQUE],
                                          filters_params=[unique_filter_params]), None)

        if found_new is not None:
            return NewsService._render_new(found_new)
        else:
            raise KeyError(f'New with title {title} not found')

    async def get_news_filtered(self, source: str = None, hydration: bool = None,
                                sentiment: Tuple[float, bool] = None, from_date: float = None,
                                to_date: float = None) -> Iterator[New]:
        """
        Filter news

        Args:
            source: news source filter
            hydration: news hydration flag filter
            sentiment: news sentiment threshold filter
            from_date: news start date to filter
            to_date: news end date to filter

        Returns: filtered news
        """
        filter_types = list()
        filters_params = list()

        if source is not None:
            source_filter_types, source_filter_params = await self._build_source_filter(source)
            filter_types.append(source_filter_types)
            filters_params.append(source_filter_params)

        if hydration is not None:
            hydration_filter_types, hydration_filter_params = await self._build_hydration_filter(hydration)
            filter_types.append(hydration_filter_types)
            filters_params.append(hydration_filter_params)

        if sentiment is not None and sentiment[0] is not None:
            sentiment_filter_types, sentiment_filter_params = await self._build_sentiment_filter(*sentiment)
            filter_types.append(sentiment_filter_types)
            filters_params.append(sentiment_filter_params)

        if from_date is not None or to_date is not None:
            date_filter_types, date_filter_params = await self._build_date_filter(from_date, to_date)
            filter_types.append(date_filter_types)
            filters_params.append(date_filter_params)

        return NewsService._render_news_list(self._client.get(filter_types, filters_params))

    @staticmethod
    async def _build_source_filter(source: str) -> Tuple[StorageFilterType, FixedDict]:
        """
        Build source field filter with the specified source

        Args:
            source: source to filter with

        Returns: source filter components

        """
        unique_filter_params = None
        if source is not None:
            unique_filter_params = StorageFilterType.UNIQUE.params
            unique_filter_params['key'] = 'source'
            unique_filter_params['value'] = source

        return StorageFilterType.UNIQUE, unique_filter_params

    @staticmethod
    async def _build_hydration_filter(hydration: bool) -> Tuple[StorageFilterType, FixedDict]:
        """
        Build hydration field filter with the specified source

        Args:
            hydration: source to filter with

        Returns: hydration filter components

        """
        unique_filter_params = None
        if hydration is not None:
            unique_filter_params = StorageFilterType.UNIQUE.params
            unique_filter_params['key'] = 'hydrated'
            unique_filter_params['value'] = hydration

        return StorageFilterType.UNIQUE, unique_filter_params

    @staticmethod
    async def _build_sentiment_filter(sentiment: float, higher: bool) -> Tuple[StorageFilterType, FixedDict]:
        """
        Build sentiment field filter with the specified source

        Args:
            sentiment: sentiment to filter with
            higher: True if greater values desired, False otherwise

        Returns: sentiment filter components

        """
        range_filter_params = None
        if sentiment is not None:
            range_filter_params = StorageFilterType.RANGE.params
            range_filter_params['key'] = 'sentiment'

            if higher:
                range_filter_params['lower'] = sentiment
            else:
                range_filter_params['upper'] = sentiment

        return StorageFilterType.RANGE, range_filter_params

    @staticmethod
    async def _build_date_filter(from_date: float, to_date: float) -> Tuple[StorageFilterType, FixedDict]:
        """
        Build date field filter with the specified source

        Args:
            from_date: start date to filter with
            to_date: end date to filter with

        Returns: date filter components

        """
        range_filter_params = None
        if from_date is not None or to_date is not None:
            range_filter_params = StorageFilterType.RANGE.params
            range_filter_params['key'] = 'date'
            range_filter_params['upper'] = to_date
            range_filter_params['lower'] = from_date

        return StorageFilterType.RANGE, range_filter_params

    def consume_new_inserts(self) -> Iterator[dict]:
        """
        Consume the new insertions

        Returns: an iterator to the inserted news

        """
        yield from self._client.consume_inserts()

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
