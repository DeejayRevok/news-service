from unittest import TestCase
from unittest.mock import patch

from aiounittest import async_test
from asynctest import patch as async_patch
from news_service_lib import NlpServiceService
from news_service_lib.models import New


class TestNLPService(TestCase):

    TEST_NEW = New(title='Test_title', content='Test_content', date=112341234.0, categories=['Test_category'])

    @patch('news_service_lib.nlp_service_service.get_system_auth_token')
    @async_patch('aiohttp.ClientSession.put')
    @async_test
    async def test_hydrate_new_success(self, mock_put, mock_get_token):
        pass