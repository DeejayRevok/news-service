import unittest
from datetime import datetime
from unittest.mock import patch

from infrastructure.storage.filters.storage_filter_type import StorageFilterType
from lib.fixed_dict import FixedDict
from services.event_service import EventService

mocked_event = {"base_event": {"base_event_id": "291", "sell_mode": "online", "title": "Concert",
                               "event": {"event_date": 1561921200, "event_id": "291", "sell_from": 1404165600,
                                         "sell_to": 1561917600, "sold_out": "false", "zone": [
                                       {"capacity": "243", "max_price": "20.00", "name": "Platea", "numbered": "true",
                                        "zone_id": "40"},
                                       {"capacity": "100", "max_price": "0.00", "name": "test", "numbered": "false",
                                        "zone_id": "38"},
                                       {"capacity": "90", "max_price": "0.00", "name": "A28", "numbered": "true",
                                        "zone_id": "30"}]}}}


class TestEventService(unittest.TestCase):

    @patch('infrastructure.storage.storage.Storage')
    def test_save_event(self, client):
        event_service = EventService(client)
        event_service.save_event(mocked_event)
        client.save.assert_called_with(mocked_event, exist_filter=StorageFilterType.UNIQUE,
                                       exist_params=FixedDict(dict(key='base_event.base_event_id', value='291')))

    @patch('infrastructure.storage.storage.Storage')
    @patch.object(EventService, 'render_event_list')
    def test_get_events_empty(self, client, event_service_mocked):
        event_service = EventService(client)
        event_service.render_event_list = event_service_mocked.render_event_list
        event_service.get_events()
        client.get.assert_called_with([StorageFilterType.UNIQUE],
                                      [FixedDict(dict(key='base_event.sell_mode', value='online'))])

    @patch('infrastructure.storage.storage.Storage')
    @patch.object(EventService, 'render_event_list')
    def test_get_events_range(self, client, event_service_mocked):
        event_service = EventService(client)
        event_service.render_event_list = event_service_mocked.render_event_list
        start = 1
        end = 2
        event_service.get_events(start=start, end=end)
        client.get.assert_called_with([StorageFilterType.RANGE, StorageFilterType.UNIQUE],
                                      [FixedDict(dict(key='base_event.event.event_date', upper=end, lower=start)),
                                       FixedDict(dict(key='base_event.sell_mode', value='online'))])

        event_service.get_events(start=start)
        client.get.assert_called_with([StorageFilterType.RANGE, StorageFilterType.UNIQUE],
                                      [FixedDict(dict(key='base_event.event.event_date', upper=None, lower=start)),
                                       FixedDict(dict(key='base_event.sell_mode', value='online'))])

        event_service.get_events(end=end)
        client.get.assert_called_with([StorageFilterType.RANGE, StorageFilterType.UNIQUE],
                                      [FixedDict(dict(key='base_event.event.event_date', upper=end, lower=None)),
                                       FixedDict(dict(key='base_event.sell_mode', value='online'))])

    def test_render_events(self):
        mocked_event_date = mocked_event['base_event']['event']['event_date']
        mocked_event_sell_from = mocked_event['base_event']['event']['sell_from']
        mocked_event_sell_to = mocked_event['base_event']['event']['sell_to']

        rendered_event_date = datetime.fromtimestamp(mocked_event_date).strftime(EventService.DATE_FORMAT)
        rendered_event_sell_from = datetime.fromtimestamp(mocked_event_sell_from).strftime(EventService.DATE_FORMAT)
        rendered_event_sell_to = datetime.fromtimestamp(mocked_event_sell_to).strftime(EventService.DATE_FORMAT)

        rendered_event = next(EventService.render_event_list([mocked_event]), None)

        assert rendered_event is not None
        assert rendered_event['base_event']['event']['event_date'] == rendered_event_date
        assert rendered_event['base_event']['event']['sell_from'] == rendered_event_sell_from
        assert rendered_event['base_event']['event']['sell_to'] == rendered_event_sell_to


if __name__ == '__main__':
    unittest.main()
