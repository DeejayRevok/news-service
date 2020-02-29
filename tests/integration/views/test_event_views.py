import unittest
from time import mktime, strptime
from unittest.mock import patch

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from aiohttp.web_app import Application

from services.event_service import EventService
from webapp.middlewares import middleware_factory
from webapp.views.events_view import setup_routes
from webapp.views.events_view import ROOT_PATH
from webapp.definitions import API_VERSION

MOCKED_RESPONSE = [{
    'test': 'test'
}, {
    'test2': 'test2'
}]

EXCEPTION_MESSAGE = 'test'


def raise_exception(**_):
    raise Exception(EXCEPTION_MESSAGE)


class TestEventsView(AioHTTPTestCase):

    @patch.object(EventService, 'get_events')
    async def get_application(self, mocked_event_service):
        """
        Override the get_app method to return your application.
        """
        mocked_event_service.get_events.return_value = iter(MOCKED_RESPONSE)
        self.mocked_event_service = mocked_event_service
        app = Application()
        app['event_service'] = mocked_event_service
        app.middlewares.append(middleware_factory)
        setup_routes(app)
        return app

    @unittest_run_loop
    async def test_get_events(self):
        """
        Test the get events REST endpoint without params
        """
        resp = await self.client.get(f'/{API_VERSION}{ROOT_PATH}')
        self.assertEqual(resp.status, 200)
        response_content = await resp.json()
        self.assertEqual(response_content, list(MOCKED_RESPONSE))
        self.mocked_event_service.get_events.assert_called_with(start=None, end=None)

    @unittest_run_loop
    async def test_get_events_filtered(self):
        """
        Test the get events REST endpoint with query parameters
        """
        query_params = dict(start_date='2019-06-30T20:00:00', end_date='2019-06-30T22:00:00')
        start_parsed = mktime(strptime(query_params['start_date'], '%Y-%m-%dT%H:%M:%S'))
        end_parsed = mktime(strptime(query_params['end_date'], '%Y-%m-%dT%H:%M:%S'))
        resp = await self.client.get(f'/{API_VERSION}{ROOT_PATH}', params=query_params)
        self.assertEqual(resp.status, 200)
        self.mocked_event_service.get_events.assert_called_with(start=start_parsed, end=end_parsed)

    @unittest_run_loop
    async def test_get_events_wrong_request(self):
        """
        Test the get events REST endpoint with wrong parameters
        """
        query_params = dict(start_date='WRONG_PARAM', end_date='WRONG_PARAM')
        resp = await self.client.get(f'/{API_VERSION}{ROOT_PATH}', params=query_params)
        self.assertEqual(resp.status, 400)
        self.mocked_event_service.assert_not_called()

    @unittest_run_loop
    async def test_get_events_error(self):
        """
        Test the get events REST endpoint failed
        """
        self.mocked_event_service.get_events = raise_exception
        self.app['event_service'] = self.mocked_event_service
        resp = await self.client.get(f'/{API_VERSION}{ROOT_PATH}')
        response_content = await resp.json()
        self.assertEqual(resp.status, 500)
        self.assertEqual(response_content['detail'], EXCEPTION_MESSAGE)


if __name__ == '__main__':
    unittest.main()