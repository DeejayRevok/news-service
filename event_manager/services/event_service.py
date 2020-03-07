"""
Event service module
"""
from datetime import datetime
from typing import Iterator

from event_manager.infrastructure.storage.filters.storage_filter_type import StorageFilterType
from event_manager.infrastructure.storage.mongo_storage import MongoStorage
from event_manager.infrastructure.storage.storage import Storage


class EventService:
    """
    Class used to manage the interaction with the events
    """
    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, client: Storage):
        """
        Initialize the event service with the specified storage client

        Args:
            client: storage client
        """
        self._client = client
        if isinstance(self._client, MongoStorage):
            self._client.set_collection('event')

    async def save_event(self, event: dict):
        """
        Persist the specified event

        Args:
            event: event to persist

        """
        exist_filter_params = StorageFilterType.UNIQUE.params
        exist_filter_params['key'] = 'base_event.base_event_id'
        exist_filter_params['value'] = event['base_event']['base_event_id']
        self._client.save(event, exist_filter=StorageFilterType.UNIQUE, exist_params=exist_filter_params)

    async def get_events(self, start: int = None, end: int = None) -> Iterator[dict]:
        """
        Get events with date within the specified time range

        Args:
            start: start date timestamp of the filter range
            end: end date timestamp of the filter range

        Returns: iterator to the filtered events

        """
        filter_types = []
        filters_params = []
        if start is not None or end is not None:
            range_filter_params = StorageFilterType.RANGE.params
            range_filter_params['key'] = 'base_event.event.event_date'
            range_filter_params['upper'] = end
            range_filter_params['lower'] = start

            filter_types.append(StorageFilterType.RANGE)
            filters_params.append(range_filter_params)

        unique_filter_params = StorageFilterType.UNIQUE.params
        unique_filter_params['key'] = 'base_event.sell_mode'
        unique_filter_params['value'] = 'online'
        filter_types.append(StorageFilterType.UNIQUE)
        filters_params.append(unique_filter_params)

        return EventService.render_event_list(self._client.get(filter_types, filters_params))

    @staticmethod
    def render_event_list(event_list: Iterator[dict]) -> Iterator[dict]:
        """
        Render the events from the specified list

        Args:
            event_list: events to render

        Returns: iterator to the rendered events

        """
        for event in event_list:
            yield EventService.render_event(event)

    @staticmethod
    def render_event(event: dict) -> dict:
        """
        Render a single event dict changing the timestamps with the dates

        Args:
            event: event to render

        Returns: rendered event

        """
        event['base_event']['event']['event_date'] = datetime.fromtimestamp(
            event['base_event']['event']['event_date']).strftime(EventService.DATE_FORMAT)
        event['base_event']['event']['sell_from'] = datetime.fromtimestamp(
            event['base_event']['event']['sell_from']).strftime(EventService.DATE_FORMAT)
        event['base_event']['event']['sell_to'] = datetime.fromtimestamp(
            event['base_event']['event']['sell_to']).strftime(EventService.DATE_FORMAT)
        return event
