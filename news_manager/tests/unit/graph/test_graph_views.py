"""
GraphQL views tests module
"""
import asyncio
from unittest import TestCase
from unittest.mock import patch

from aiohttp.web_app import Application
from aiounittest import async_test
from graphql.error import GraphQLLocatedError

from news_manager.webapp.graph.graphql_views import setup_routes, schema, GRAPHIQL_JWT_TEMPLATE, error_formatter


class TestGraphViews(TestCase):
    """
    Graph views test cases implementation
    """
    @patch('news_manager.webapp.graph.graphql_views.AsyncioExecutor')
    @patch('news_manager.webapp.graph.graphql_views.GraphQLView')
    @async_test
    async def test_setup_routes(self, graph_view_mock, executor_mock):
        """
        Test the setup routes setups the GraphQL view with the provided app, the predefined schema
        and the predefined template
        """
        test_app = Application()
        setup_routes(test_app)
        graph_view_mock.attach.assert_called_with(test_app,
                                                  schema=schema,
                                                  graphiql=True,
                                                  graphiql_template=GRAPHIQL_JWT_TEMPLATE,
                                                  route_path='/graphql',
                                                  executor=executor_mock(loop=asyncio.get_event_loop()),
                                                  enable_async=True,
                                                  error_formatter=error_formatter)

    def test_error_formatter(self):
        """
        Test the error formatter with a GraphQLError returns the inner original error dict like formatted
        """
        original_test_error = Exception('Test exception')
        test_error = GraphQLLocatedError(nodes=[], original_error=original_test_error)
        formatted_error = error_formatter(test_error)
        self.assertEqual(formatted_error['error'], original_test_error.__class__.__name__)
        self.assertEqual(formatted_error['detail'], str(original_test_error))
