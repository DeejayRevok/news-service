"""
Middlewares testing module
"""
import json
from unittest.mock import patch

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp.web_app import Application
from aiohttp.web_exceptions import HTTPUnauthorized
from aiohttp.web_response import Response

from uaa.webapp.middlewares import error_middleware


class MockRequest:
    """
    Mocked web request
    """
    def __init__(self):
        self.method = 'TestMethod'
        self.rel_url = 'TestURL'


class TestMiddlewares(AioHTTPTestCase):
    """
    Test case for middlewares module
    """
    EXCEPTION_DETAILS = 'Test exception'

    @patch('elasticapm.middleware.ElasticAPM')
    async def get_application(self, mock_apm_client):
        """
        Override the get_app method to return the mocked application.
        """
        app = Application()
        app['apm'] = mock_apm_client
        return app

    @unittest_run_loop
    async def test_error_middleware_exception(self):
        """
        Test the error middleware when handler raises an exception
        """

        async def mock_handler(_):
            raise Exception(self.EXCEPTION_DETAILS)

        error_middle = await error_middleware(self.app, mock_handler)
        error_json = await error_middle(MockRequest())
        self.assertIsInstance(error_json, Response)
        self.assertEqual(error_json.status, 500)
        self.assertEqual(json.loads(str(error_json.body, 'UTF-8')),
                         dict(error=Exception.__name__, detail=self.EXCEPTION_DETAILS))

    @unittest_run_loop
    async def test_error_middleware_httpexception_unauthorized(self):
        """
        Test the error middleware when handler raises an httpexception
        """

        async def mock_handler(_):
            raise HTTPUnauthorized(reason=self.EXCEPTION_DETAILS)

        error_middle = await error_middleware(self.app, mock_handler)
        error_json = await error_middle(MockRequest())
        self.assertIsInstance(error_json, Response)
        self.assertEqual(error_json.status, HTTPUnauthorized.status_code)
        self.assertEqual(json.loads(str(error_json.body, 'UTF-8')),
                         dict(error=HTTPUnauthorized.__name__, detail=self.EXCEPTION_DETAILS))
