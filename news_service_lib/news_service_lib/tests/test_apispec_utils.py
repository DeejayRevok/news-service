"""
Apispec utils tests module
"""
from unittest import TestCase
from unittest.mock import patch, call

from aiohttp.web_app import Application

from ..apispec_utils import setup_aiohttp_apispec_mod


class TestApiSpecUtils(TestCase):

    @patch('news_service_lib.apispec_utils.Template')
    def test_apispec_static_url(self, template_mock):
        """
        Test the setup apispec mod with static base url ads it as a prefix
        """
        static_url = '/static_url'
        url = '/url'
        static_path = '/static_path'
        app = Application()
        with patch('news_service_lib.apispec_utils.open', create=True) as _:
            setup_aiohttp_apispec_mod(app=app, url=url, static_base_url=static_url, static_path=static_path,
                                      swagger_path='/test')
            self.assertIn(
                call().render(path=static_url + url, static=static_url + static_path), template_mock.mock_calls)

    @patch('news_service_lib.apispec_utils.Template')
    def test_apispec_non_static_url(self, template_mock):
        """
        Test the setup apispec mod without static base url set path variable of template as url and
        static template variable as the static path
        """
        url = '/url'
        static_path = '/static_path'
        app = Application()
        with patch('news_service_lib.apispec_utils.open', create=True) as _:
            setup_aiohttp_apispec_mod(app=app, url=url, static_path=static_path,
                                      swagger_path='/test')
            self.assertIn(
                call().render(path=url, static=static_path), template_mock.mock_calls)
