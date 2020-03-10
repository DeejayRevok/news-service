"""
User views module
"""
from aiohttp.web_app import Application
from aiohttp.web_exceptions import HTTPBadRequest
from aiohttp.web_request import Request
from aiohttp.web_response import Response, json_response
from aiohttp_apispec import docs, request_schema

from uaa.lib.aio_class_route_table import ClassRouteTableDef
from uaa.log_config import get_logger
from uaa.webapp.definitions import API_VERSION, login_required
from uaa.webapp.request_schemas.user_request_schemas import PostCreateUserSchema

ROOT_PATH = '/api/users'
LOGGER = get_logger()
ROUTES = ClassRouteTableDef()


class UserViews:
    """
    User REST endpoint views handler
    """

    def __init__(self, app: Application):
        """
        Initialize the user views handler

        Args:
            app: application associated
        """
        self.user_service = app['user_service']

    @docs(
        tags=['Users'],
        summary="Get user data",
        description="Get authenticated user data",
        security=[{'ApiKeyAuth': []}]
    )
    @ROUTES.get(f'/{API_VERSION}{ROOT_PATH}/data', allow_head=False)
    async def get_user_data(self, request: Request) -> Response:
        """
        Request to get an user identified by its username

        Args:
            request: input REST request

        Returns: json REST response with the queried user

        """

        @login_required
        async def request_executor(inner_request):
            LOGGER.info('REST request to get one user')

            return json_response(dict(inner_request.user), status=200)

        return await request_executor(request)

    @docs(
        tags=['Users'],
        summary="Create user",
        description="Create a new user"
    )
    @request_schema(PostCreateUserSchema)
    @ROUTES.post(f'/{API_VERSION}{ROOT_PATH}')
    async def post_create_user(self, request: Request) -> Response:
        """
        Request to create an user

        Args:
            request: input REST request

        Returns: json REST response with the created user

        """
        LOGGER.info('REST request to create user')

        try:
            username = request['data']['username']
            password = request['data']['password']
        except Exception as ex:
            raise HTTPBadRequest(text=str(ex))

        user_created = await self.user_service.create_user(username, password)

        return json_response(dict(user_created), status=200)


def setup_routes(app: Application):
    """
    Add the class routes to the specified application

    Args:
        app: application to add routes

    """
    ROUTES.clean_routes()
    ROUTES.add_class_routes(UserViews(app))
    app.router.add_routes(ROUTES)
