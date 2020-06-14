"""
GraphQL queries tests module
"""
import asyncio
from unittest import TestCase
from unittest.mock import MagicMock

from aiohttp.web_app import Application
from graphene.test import Client
from graphql.execution.executors.asyncio import AsyncioExecutor
from news_service_lib.models import New

from news_manager.webapp.graph.graphql_views import schema


class TestNewsQueries(TestCase):
    """
    GraphQL news queries test cases implementation
    """
    TEST_NEW = New(title='Test1', content='Test1', source='Test1', date=101001.10)
    TEST_ANOTHER_NEW = New(title='Test2', content='Test2', source='Test2', date=101001.10)

    def test_get_new_title(self):
        """
        Test the new(title) query queries the new with the specified title and returns it
        """
        async def new_response():
            return self.TEST_NEW

        test_app = Application()
        news_service_mock = MagicMock()
        news_service_mock.get_new_by_title.return_value = new_response()
        test_app['news_service'] = news_service_mock

        request_mock = MagicMock()
        request_mock.app = test_app
        request_mock.user = True

        client = Client(schema)
        executed = client.execute('''{ 
                                        new(title: "test_query_title"){
                                            title
                                        }
                                      }''',
                                  context_value=dict(request=request_mock),
                                  executor=AsyncioExecutor(loop=asyncio.get_event_loop()))

        news_service_mock.get_new_by_title.assert_called_with("test_query_title")
        expected_data = dict(new=dict(title=self.TEST_NEW.title))
        self.assertEqual(executed['data'], expected_data)

    def test_get_news(self):
        """
        Test the news query queries the news with the specified arguments and returns the results
        """
        async def news_response():
            return [self.TEST_NEW, self.TEST_ANOTHER_NEW]

        test_app = Application()
        news_service_mock = MagicMock()
        news_service_mock.get_news_filtered.return_value = news_response()
        test_app['news_service'] = news_service_mock

        request_mock = MagicMock()
        request_mock.app = test_app
        request_mock.user = True

        client = Client(schema)
        executed = client.execute('''{ 
                                        news(source: "test_source"){
                                            title
                                        }
                                      }''',
                                  context_value=dict(request=request_mock),
                                  executor=AsyncioExecutor(loop=asyncio.get_event_loop()))

        news_service_mock.get_news_filtered.assert_called_with(from_date=None,
                                                               hydration=None,
                                                               sentiment=(None, True),
                                                               source='test_source',
                                                               to_date=None)

        expected_data = dict(news=[dict(title=self.TEST_NEW.title), dict(title=self.TEST_ANOTHER_NEW.title)])
        self.assertEqual(executed['data'], expected_data)

