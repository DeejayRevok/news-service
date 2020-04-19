import asyncio
import unittest
from unittest.mock import patch

from news_manager.infrastructure.storage.filters.storage_filter_type import StorageFilterType
from news_service_lib.models.new import New
from news_manager.lib.fixed_dict import FixedDict
from news_manager.services.news_service import NewsService

MOCKED_NEW = New(title='Test title', content='Test content', categories=['Test category'], date=10101010.00)


class TestNewsService(unittest.TestCase):
    """
    News service test cases implementation
    """
    @patch('news_manager.infrastructure.storage.storage.Storage')
    def test_save_new(self, client):
        """
        Test persisting new
        """
        news_service = NewsService(client)

        loop = asyncio.new_event_loop()
        loop.run_until_complete(news_service.save_new(MOCKED_NEW))

        client.save.assert_called_with(dict(MOCKED_NEW), exist_filter=StorageFilterType.UNIQUE,
                                       exist_params=FixedDict(dict(key='title', value='Test title')))

    @patch('news_manager.infrastructure.storage.storage.Storage')
    @patch.object(NewsService, '_render_news_list')
    def test_get_news_empty(self, client, news_service_mocked):
        """
        Test find news without filter
        """
        news_service = NewsService(client)
        news_service._render_news_list = news_service_mocked._render_news_list

        loop = asyncio.new_event_loop()
        loop.run_until_complete(news_service.get_news())

        client.get.assert_called()

    @patch('news_manager.infrastructure.storage.storage.Storage')
    @patch.object(NewsService, '_render_news_list')
    def test_get_news_range(self, client, news_service_mocked):
        """
        Test find news with range filter
        """
        news_service = NewsService(client)
        news_service._render_news_list = news_service_mocked._render_news_list
        start = 1
        end = 2

        loop = asyncio.new_event_loop()
        loop.run_until_complete(news_service.get_news(start=start, end=end))

        client.get.assert_called_with([StorageFilterType.RANGE],
                                      [FixedDict(dict(key='date', upper=end, lower=start))])

        loop = asyncio.new_event_loop()
        loop.run_until_complete(news_service.get_news(start=start))

        client.get.assert_called_with([StorageFilterType.RANGE],
                                      [FixedDict(dict(key='date', upper=None, lower=start))])

        loop = asyncio.new_event_loop()
        loop.run_until_complete(news_service.get_news(end=end))

        client.get.assert_called_with([StorageFilterType.RANGE],
                                      [FixedDict(dict(key='date', upper=end, lower=None))])

    def test_render_news(self):
        """
        Test news rendering
        """

        rendered_new = next(NewsService._render_news_list([dict(MOCKED_NEW)]), None)

        self.assertIsNotNone(rendered_new)
        self.assertIsInstance(rendered_new, New)


if __name__ == '__main__':
    unittest.main()
