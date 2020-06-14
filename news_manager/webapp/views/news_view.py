"""
News views module
"""
from time import strptime, mktime

from aiohttp.web_app import Application
from aiohttp.web_exceptions import HTTPBadRequest
from aiohttp.web_request import Request
from aiohttp.web_response import json_response, Response
from aiohttp_apispec import docs
from news_service_lib import ClassRouteTableDef, login_required

from news_manager.log_config import get_logger
from news_manager.webapp.definitions import API_VERSION

ROOT_PATH = '/api/news'
LOGGER = get_logger()
ROUTES = ClassRouteTableDef()


class NewsViews:
    """
    News REST endpoint views handler
    """
    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, app: Application):
        """
        Initialize the news views handler

        Args:
            app: application associated
        """
        self.news_service = app['news_service']

    @docs(
        tags=['News'],
        summary="News list",
        description="Get available news",
        parameters=[{
            'in': 'query',
            'name': 'start_date',
            'type': 'string',
            'format': 'date-time',
            'description': 'Start date to filter news',
            'required': False
        }, {
            'in': 'query',
            'name': 'end_date',
            'type': 'string',
            'format': 'date-time',
            'description': 'End date to filter news',
            'required': False
        }],
        security=[{'ApiKeyAuth': []}]
    )
    @ROUTES.get(f'/{API_VERSION}{ROOT_PATH}', allow_head=False)
    async def get_news(self, request: Request) -> Response:
        """
        Request to get stored news

        Args:
            request: input REST request

        Returns: json REST response with the queried news

        """

        @login_required
        async def request_executor(inner_request):
            LOGGER.info('REST request to get all news')

            try:
                start_date = mktime(strptime(inner_request.rel_url.query['start_date'],
                                             self.DATE_FORMAT)) if 'start_date' in inner_request.rel_url.query else None
                end_date = mktime(strptime(inner_request.rel_url.query['end_date'],
                                           self.DATE_FORMAT)) if 'end_date' in inner_request.rel_url.query else None
            except Exception as ex:
                raise HTTPBadRequest(text=str(ex))

            news = list(map(lambda new: new.dto(self.DATE_FORMAT),
                            await self.news_service.get_news_filtered(from_date=start_date, to_date=end_date)))

            return json_response(news, status=200)

        return await request_executor(request)


def setup_routes(app: Application):
    """
    Add the class routes to the specified application

    Args:
        app: application to add routes

    """
    ROUTES.clean_routes()
    ROUTES.add_class_routes(NewsViews(app))
    app.router.add_routes(ROUTES)
