"""
Event views module
"""
from time import strptime, mktime

from aiohttp.web_app import Application
from aiohttp.web_exceptions import HTTPBadRequest
from aiohttp.web_request import Request
from aiohttp.web_response import json_response, Response
from aiohttp_apispec import docs

from lib.sources.aio_class_route_table import ClassRouteTableDef
from event_manager.log_config import get_logger
from event_manager.webapp.definitions import API_VERSION, login_required

ROOT_PATH = '/api/events'
LOGGER = get_logger()
ROUTES = ClassRouteTableDef()


class EventViews:
    """
    Event REST endpoint views handler
    """

    def __init__(self, app: Application):
        """
        Initialize the event views handler

        Args:
            app: application associated
        """
        self.event_service = app['event_service']

    @docs(
        tags=['Events'],
        summary="Event list",
        description="Get available events",
        parameters=[{
            'in': 'query',
            'name': 'start_date',
            'type': 'string',
            'format': 'date-time',
            'description': 'Start date to filter events',
            'required': False
        }, {
            'in': 'query',
            'name': 'end_date',
            'type': 'string',
            'format': 'date-time',
            'description': 'End date to filter events',
            'required': False
        }],
        security=[{'ApiKeyAuth': []}]
    )
    @ROUTES.get(f'/{API_VERSION}{ROOT_PATH}', allow_head=False)
    async def get_events(self, request: Request) -> Response:
        """
        Request to get stored events

        Args:
            request: input REST request

        Returns: json REST response with the queried events

        """

        @login_required
        async def request_executor(inner_request):
            LOGGER.info('REST request to get all events')

            try:
                start_date = mktime(strptime(inner_request.rel_url.query['start_date'],
                                             '%Y-%m-%dT%H:%M:%S')) if 'start_date' in inner_request.rel_url.query else None
                end_date = mktime(strptime(inner_request.rel_url.query['end_date'],
                                           '%Y-%m-%dT%H:%M:%S')) if 'end_date' in inner_request.rel_url.query else None
            except Exception as ex:
                raise HTTPBadRequest(text=str(ex))

            events = list(await self.event_service.get_events(start=start_date, end=end_date))

            return json_response(events, status=200)

        return await request_executor(request)


def setup_routes(app: Application):
    """
    Add the class routes to the specified application

    Args:
        app: application to add routes

    """
    ROUTES.clean_routes()
    ROUTES.add_class_routes(EventViews(app))
    app.router.add_routes(ROUTES)
