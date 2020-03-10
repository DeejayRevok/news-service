"""
Authentication service test cases
"""
import asyncio
from unittest import TestCase, main
from unittest.mock import patch

from uaa.models.user import User
from uaa.services.authentication_service import AuthService

TEST_USERNAME = 'test_user'
TEST_PASSWORD = 'test_password'


class TestUserService(TestCase):

    @patch('uaa.services.authentication_service.UserService')
    def setUp(self, service_mock):
        """
        Set up each test environment
        """
        self.service_mock = service_mock
        self.auth_service = AuthService(service_mock)

    @patch('uaa.services.authentication_service.generate_token')
    @patch('uaa.services.authentication_service.hash_password')
    def test_authenticate_successful(self, hash_mock, generate_token_mock):
        """
        Check if authentication successful returns the authentication token
        """
        mock_hash_pass = 'mocked_hash_pass'
        test_token = 'test_token'

        async def mock_user_by_name_response():
            return User(id=1, username=TEST_USERNAME, password=mock_hash_pass)

        self.service_mock.get_user_by_name.return_value = mock_user_by_name_response()
        hash_mock.return_value = mock_hash_pass
        generate_token_mock.return_value = bytes(test_token, 'UTF-8')
        loop = asyncio.new_event_loop()
        authentication_token = loop.run_until_complete(self.auth_service.authenticate(TEST_USERNAME, TEST_PASSWORD))
        self.assertEqual(authentication_token['token'], test_token)

    @patch('uaa.services.authentication_service.hash_password')
    def test_authenticate_fails(self, hash_mock):
        """
        Check if the authentication failed raises error
        """
        mock_hash_pass = 'mocked_hash_pass'

        async def mock_user_by_name_response():
            return User(id=1, username=TEST_USERNAME, password=mock_hash_pass)

        self.service_mock.get_user_by_name.return_value = mock_user_by_name_response()
        hash_mock.return_value = 'wrong_pass'
        loop = asyncio.new_event_loop()
        with self.assertRaises(ValueError):
            loop.run_until_complete(self.auth_service.authenticate(TEST_USERNAME, TEST_PASSWORD))

    @patch('uaa.services.authentication_service.decode_token')
    def test_validate_token_successfull(self, decode_token_mock):
        """
        Check if the successful token validation returns user data
        """
        mock_hash_pass = 'mocked_hash_pass'

        async def mock_user_by_id_response():
            return User(id=1, username=TEST_USERNAME, password=mock_hash_pass)

        self.service_mock.get_user_by_id.return_value = mock_user_by_id_response()
        decode_token_mock.return_value = dict(user_id=1)
        loop = asyncio.new_event_loop()
        validated_user = loop.run_until_complete(self.auth_service.validate_token('test_token'))
        self.assertEqual(validated_user.username, TEST_USERNAME)

    @patch('uaa.services.authentication_service.decode_token')
    def test_validate_token_fails(self, decode_token_mock):
        """
        Check if the failed token validation raises error
        """
        async def mock_user_by_id_response():
            return None

        self.service_mock.get_user_by_id.return_value = mock_user_by_id_response()
        decode_token_mock.return_value = dict(user_id=1)
        loop = asyncio.new_event_loop()
        with self.assertRaises(ValueError):
            loop.run_until_complete(self.auth_service.validate_token('test_token'))


if __name__ == '__main__':
    main()
