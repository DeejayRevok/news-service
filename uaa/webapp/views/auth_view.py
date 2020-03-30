"""
Authentication views module
"""
from aiohttp.web_app import Application
from aiohttp.web_exceptions import HTTPBadRequest
from aiohttp.web_request import Request
from aiohttp.web_response import Response, json_response
from aiohttp_apispec import docs, request_schema

from lib.sources.aio_class_route_table import ClassRouteTableDef
from uaa.log_config import get_logger
from uaa.webapp.definitions import API_VERSION
from uaa.webapp.request_schemas.auth_request_schemas import PostAuthSchema, PostValidateTokenSchema

ROOT_PATH = '/api/auth'
LOGGER = get_logger()
ROUTES = ClassRouteTableDef()


class AuthViews:
    """
    Authentication REST endpoint views handler
    """

    def __init__(self, app: Application):
        """
        Initialize the authentication views handler

        Args:
            app: application associated
        """
        self.auth_service = app['auth_service']

    @docs(
        tags=['Authentication'],
        summary="Authenticate user",
        description="Authenticate an user by username and password"
    )
    @request_schema(PostAuthSchema)
    @ROUTES.post(f'/{API_VERSION}{ROOT_PATH}')
    async def authenticate(self, request: Request) -> Response:
        """
        Request to authenticate an user

        Args:
            request: input REST request

        Returns: json REST response with the authentication token

        """
        LOGGER.info('REST request to authenticate an user')

        try:
            username = request['data']['username']
            password = request['data']['password']
        except Exception as ex:
            raise HTTPBadRequest(text=str(ex))

        token_response = await self.auth_service.authenticate(username, password)

        return json_response(token_response, status=200)

    @docs(
        tags=['Authentication'],
        summary="Validate token",
        description="Validate JWT token"
    )
    @request_schema(PostValidateTokenSchema)
    @ROUTES.post(f'/{API_VERSION}{ROOT_PATH}/token')
    async def validate_token(self, request: Request) -> Response:
        """
        Request to validate a JWT token

        Args:
            request: input REST request

        Returns: json REST response with the authenticated user data

        """
        LOGGER.info('REST request to validate JWT token')

        try:
            token = request['data']['token']
        except Exception as ex:
            raise HTTPBadRequest(text=str(ex))

        user = await self.auth_service.validate_token(token)

        return json_response(dict(user), status=200)


def setup_routes(app: Application):
    """
    Add the class routes to the specified application

    Args:
        app: application to add routes

    """
    ROUTES.clean_routes()
    ROUTES.add_class_routes(AuthViews(app))
    app.router.add_routes(ROUTES)
