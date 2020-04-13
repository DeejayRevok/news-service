"""
UAA service module tests
"""
from unittest import TestCase
from unittest.mock import patch

from aiohttp.web_exceptions import HTTPUnauthorized, HTTPInternalServerError
from aiounittest import async_test
from asynctest import CoroutineMock, patch as async_patch
from news_service_lib.uaa_service import UaaService, get_system_auth_token, get_uaa_service


class TestUaaService(TestCase):
    TEST_HOST = 'test_host'
    TEST_PORT = '0'
    TEST_PROTOCOL = 'test_protocol'
    TEST_TOKEN = 'test_token'
    TEST_RESPONSE = {'id': 1}
    TEST_WRONG_RESPONSE = {'not_id': 1}

    @async_patch('aiohttp.ClientSession.post')
    @async_test
    async def test_validate_token_success(self, mock_post):
        """
        Test the validate token successful returns the response with the user id and is called accordingly
        """
        mock_post.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.json = CoroutineMock(side_effect=[self.TEST_RESPONSE])
        uaa_service = UaaService(self.TEST_PROTOCOL, self.TEST_HOST, self.TEST_PORT)
        response_json = await uaa_service.validate_token(self.TEST_TOKEN)
        mock_post.assert_called_with(
            f'{self.TEST_PROTOCOL}://{self.TEST_HOST}:{self.TEST_PORT}/{uaa_service.PATHS["validate_token"]}',
            data=dict(token=self.TEST_TOKEN))
        self.assertEqual(response_json, self.TEST_RESPONSE)

    @async_patch('aiohttp.ClientSession.post')
    @async_test
    async def test_validate_token_wrong_response(self, mock_post):
        """
        Test the validate token with response without the user id raises unauthorized error
        """
        mock_post.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.json = CoroutineMock(side_effect=[self.TEST_WRONG_RESPONSE])
        uaa_service = UaaService(self.TEST_PROTOCOL, self.TEST_HOST, self.TEST_PORT)
        with self.assertRaises(HTTPUnauthorized):
            await uaa_service.validate_token(self.TEST_TOKEN)

    @async_patch('aiohttp.ClientSession.post')
    @async_test
    async def test_validate_token_call_fail(self, mock_post):
        """
        Test the validate token call failed raises ConnectionError
        """
        mock_post.side_effect = Exception('Test')
        uaa_service = UaaService(self.TEST_PROTOCOL, self.TEST_HOST, self.TEST_PORT)
        with self.assertRaises(ConnectionError):
            await uaa_service.validate_token(self.TEST_TOKEN)

    @async_patch('aiohttp.ClientSession.post')
    @async_test
    async def test_validate_token_internal_error(self, mock_post):
        """
        Test the validate token with internal server error response raises Unauthorized
        """
        mock_post.return_value.__aenter__.return_value.status = 500
        uaa_service = UaaService(self.TEST_PROTOCOL, self.TEST_HOST, self.TEST_PORT)
        with self.assertRaises(HTTPUnauthorized):
            await uaa_service.validate_token(self.TEST_TOKEN)

    @async_patch('aiohttp.ClientSession.post')
    @async_test
    async def test_validate_token_fail_response(self, mock_post):
        """
        Test the validate token with HTTP error raises ConnectionError
        """
        mock_post.return_value.__aenter__.return_value.status = 400
        uaa_service = UaaService(self.TEST_PROTOCOL, self.TEST_HOST, self.TEST_PORT)
        with self.assertRaises(HTTPInternalServerError):
            await uaa_service.validate_token(self.TEST_TOKEN)

    @patch('news_service_lib.uaa_service.generate_token')
    def test_get_system_token(self, mocked_generate_token):
        """
        Test the get system token returns the system token
        """
        test_token = 'TEST'
        mocked_generate_token.return_value = bytes(test_token, 'UTF-8')
        token_generated = get_system_auth_token()
        self.assertEqual(token_generated, test_token)
        mocked_generate_token.assert_called_with(dict(user_id=-1000))

    def test_get_uaa_service(self):
        """
        Test the get uaa service method returns UaaService configured with the input configuration
        """
        uaa_service = get_uaa_service(dict(protocol=self.TEST_PROTOCOL, host=self.TEST_HOST, port=self.TEST_PORT))
        self.assertEqual(uaa_service._protocol, self.TEST_PROTOCOL)
        self.assertEqual(uaa_service._host, self.TEST_HOST)
        self.assertEqual(uaa_service._port, int(self.TEST_PORT))