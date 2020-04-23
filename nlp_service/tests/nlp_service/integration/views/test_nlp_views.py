"""
NLP views test case
"""
import json
from unittest import main
from unittest.mock import patch

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp.web_app import Application
from aiohttp_apispec import validation_middleware, setup_aiohttp_apispec
from news_service_lib.models import New, NLPDoc

from nlp_service.webapp.middlewares import error_middleware
from nlp_service.webapp.views.nlp_view import setup_routes, ROOT_PATH
from nlp_service.webapp.definitions import API_VERSION

MOCKED_USER = dict(username='test_user', password='test_password')


async def mock_auth_middleware(_, handler):
    """
    Mocked authentication middleware
    """

    async def middleware(request):
        request.user = MOCKED_USER
        return await handler(request)

    return middleware


class TestNlpViews(AioHTTPTestCase):
    TEST_NLP_DOC = NLPDoc(sentences=['test_sentence'], named_entities=[('test_entity_text', 'test_entity_type')])
    TEST_NEW = New(title='test_title', content='test_content', date=232421.0, categories=['test_category'], summary='',
                   sentiment=0.0)

    @patch('nlp_service.services.nlp_service.NlpService')
    @patch('elasticapm.middleware.ElasticAPM')
    async def get_application(self, mock_apm_client, nlp_service_mocked):
        """
        Override the get_app method to return your application.
        """

        async def get_processed_text_return():
            return self.TEST_NLP_DOC

        async def hydrate_return():
            """
            Test mocked asynchronous method response
            """
            pass

        self.mock_nlp_service = nlp_service_mocked
        self.mock_nlp_service.get_processed_text.return_value = get_processed_text_return()
        self.mock_nlp_service.hydrate_new.return_value = hydrate_return()
        app = Application()
        app['apm'] = mock_apm_client
        app['nlp_service'] = self.mock_nlp_service
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
    async def test_process_text(self):
        """
        Test the process text REST endpoint
        """
        test_text = 'test_text'
        resp = await self.client.post(f'/{API_VERSION}{ROOT_PATH}', data=dict(text=test_text))
        self.assertEqual(resp.status, 200)
        response_content = await resp.json()
        self.assertEqual(response_content, json.loads(json.dumps(dict(self.TEST_NLP_DOC))))

    @unittest_run_loop
    async def test_hydrate_new(self):
        """
        Test the hydrate new REST endpoint
        """
        resp = await self.client.put(f'/{API_VERSION}{ROOT_PATH}/hydrate', data=dict(self.TEST_NEW))
        self.assertEqual(resp.status, 204)
        dict_response = dict(self.TEST_NEW)
        del dict_response['hydrated']
        del dict_response['entities']
        self.mock_nlp_service.hydrate_new.assert_called_with(dict_response)


if __name__ == '__main__':
    main()
