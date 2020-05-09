"""
Authentication views test cases
"""
from unittest import main
from unittest.mock import patch

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp.web_app import Application
from aiohttp_apispec import validation_middleware, setup_aiohttp_apispec

from uaa.models.user import User
from uaa.webapp.middlewares import error_middleware
from uaa.webapp.definitions import API_VERSION
from uaa.webapp.views.auth_view import setup_routes, ROOT_PATH

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
    User views test cases
    """
    @patch('uaa.services.authentication_service.AuthService')
    @patch('elasticapm.middleware.ElasticAPM')
    async def get_application(self, mock_apm_client, mock_auth_service):
        """
        Override the get_app method to return your application.
        """

        async def mock_auth_response():
            return dict(token='test_token')

        async def mock_validate_token_response():
            return dict(id=1, username='token')

        mock_auth_service.authenticate.return_value = mock_auth_response()
        mock_auth_service.validate_token.return_value = mock_validate_token_response()
        app = Application()
        app['apm'] = mock_apm_client
        app['auth_service'] = mock_auth_service
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
    async def test_authenticate(self):
        """
        Test the authenticate REST endpoint
        """
        resp = await self.client.post(f'/{API_VERSION}{ROOT_PATH}',
                                      data=dict(username='test_user', password='test_password'))
        self.assertEqual(resp.status, 200)
        response_content = await resp.json()
        self.assertEqual(response_content['token'], 'test_token')

    @unittest_run_loop
    async def test_validate_token(self):
        """
        Test the validate token REST endpoint
        """
        resp = await self.client.post(f'/{API_VERSION}{ROOT_PATH}/token', data=dict(token='test_token'))
        self.assertEqual(resp.status, 200)
        response_content = await resp.json()
        self.assertEqual(response_content['username'], 'token')
