"""
NLP views module
"""
from aiohttp.web_app import Application
from aiohttp.web_exceptions import HTTPBadRequest, HTTPNoContent
from aiohttp.web_request import Request
from aiohttp.web_response import json_response, Response
from aiohttp_apispec import docs, request_schema
from news_service_lib import ClassRouteTableDef, login_required

from nlp_service.webapp.definitions import API_VERSION
from nlp_service.log_config import get_logger
from nlp_service.webapp.request_schemas.nlp_request_schemas import PostGetEntitiesSchema, PutHydrateNewSchema

ROOT_PATH = '/api/nlp'
LOGGER = get_logger()
ROUTES = ClassRouteTableDef()


class NlpViews:
    """
    NLP REST endpoints views handler
    """

    def __init__(self, app: Application):
        """
        Initialize the NLP views handler

        Args:
            app: application associated
        """
        self.nlp_service = app['nlp_service']

    @docs(
        tags=['NLP'],
        summary="Get entities",
        description="Extract entities from text",
        security=[{'ApiKeyAuth': []}]
    )
    @request_schema(PostGetEntitiesSchema)
    @ROUTES.post(f'/{API_VERSION}{ROOT_PATH}/entities')
    async def get_entities(self, request: Request) -> Response:
        """
        Request to get named entities from the input text

        Args:
            request: input REST request

        Returns: json REST response with the extracted entities

        """

        @login_required
        async def request_executor(_):
            LOGGER.propagate = False
            LOGGER.info('REST request to extract named entities from text')

            try:
                text = request['data']['text']
            except Exception as ex:
                raise HTTPBadRequest(text=str(ex))

            entities = await self.nlp_service.get_named_entities(text)

            return json_response([dict(entity) for entity in entities], status=200)

        return await request_executor(request)

    @docs(
        tags=['NLP'],
        summary="Hydrate new",
        description="Hydrate new with nlp data",
        security=[{'ApiKeyAuth': []}]
    )
    @request_schema(PutHydrateNewSchema)
    @ROUTES.put(f'/{API_VERSION}{ROOT_PATH}/hydrate')
    async def hydrate_new(self, request: Request) -> Response:
        """
        Request to hydrate a new text with nlp data

        Args:
            request: input REST request

        Returns: json REST response

        """

        @login_required
        async def request_executor(_):
            LOGGER.info('REST request to hydrate a new')

            try:
                new = request['data']
            except Exception as ex:
                raise HTTPBadRequest(text=str(ex))

            await self.nlp_service.hydrate_new(new)

            return HTTPNoContent()

        return await request_executor(request)


def setup_routes(app: Application):
    """
    Add the class routes to the specified application

    Args:
        app: application to add routes

    """
    ROUTES.clean_routes()
    ROUTES.add_class_routes(NlpViews(app))
    app.router.add_routes(ROUTES)
