"""
User views test case
"""
from unittest import main
from unittest.mock import patch

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp.web_app import Application
from aiohttp_apispec import validation_middleware, setup_aiohttp_apispec

from uaa.models.user import User
from uaa.webapp.middlewares import error_middleware
from uaa.webapp.views.users_view import setup_routes
from uaa.webapp.definitions import API_VERSION
from uaa.webapp.views.users_view import ROOT_PATH

MOCKED_USER = User(username='test_user', password='test_password')


async def mock_auth_middleware(_, handler):
    """
    Mocked authentication middleware
    """
    async def middleware(request):
        request.user = dict(MOCKED_USER)
        return await handler(request)

    return middleware


class TestUserViews(AioHTTPTestCase):
    """
    User views test cases implementation
    """
    @patch('uaa.services.users_service.UserService')
    @patch('elasticapm.middleware.ElasticAPM')
    async def get_application(self, mock_apm_client, mock_user_service):
        """
        Override the get_app method to return your application.
        """

        async def mock_user_response():
            return dict(MOCKED_USER)

        mock_user_service.create_user.return_value = mock_user_response()
        self.mocked_user_service = mock_user_service
        app = Application()
        app['apm'] = mock_apm_client
        app['user_service'] = mock_user_service
        app.middlewares.append(error_middleware)
        app.middlewares.append(mock_auth_middleware)
        app.middlewares.append(validation_middleware)

        setup_aiohttp_apispec(
            app=app,
            title='API',
            version=API_VERSION,
            url=f'/{API_VERSION}/api/docs/swagger.json',
            swagger_path=f'/{API_VERSION}/api/docs/ui',
            securityDefinitions={
                'ApiKeyAuth': {'type': 'apiKey', 'name': 'X-API-Key', 'in': 'header'}
            },
        )

        setup_routes(app)
        return app

    @unittest_run_loop
    async def test_get_user_data(self):
        """
        Test the get user data REST endpoint
        """
        resp = await self.client.get(f'/{API_VERSION}{ROOT_PATH}/data')
        self.assertEqual(resp.status, 200)
        response_content = await resp.json()
        self.assertEqual(response_content['username'], MOCKED_USER.username)

    @unittest_run_loop
    async def test_create_user(self):
        """
        Test the post create user REST endpoint
        """
        resp = await self.client.post(f'/{API_VERSION}{ROOT_PATH}',
                                      data={'username': MOCKED_USER.username, 'password': MOCKED_USER.password})
        self.assertEqual(resp.status, 200)
        response_content = await resp.json()
        self.assertEqual(response_content['username'], MOCKED_USER.username)
