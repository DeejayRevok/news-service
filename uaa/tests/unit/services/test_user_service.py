"""
User service test cases
"""
import asyncio
from unittest import TestCase, main
from unittest.mock import patch

from uaa.models.user import User
from uaa.services.users_service import UserService

TEST_USERNAME = 'test_user'
TEST_PASSWORD = 'test_password'


class TestUserService(TestCase):
    """
    User service test cases
    """
    @patch('uaa.services.users_service.SqlStorage')
    def setUp(self, client_mock):
        """
        Set up each test environment
        """
        self.client_mock = client_mock
        self.user_service = UserService(client_mock)

    @patch('uaa.services.users_service.hash_password')
    def test_create_user(self, hash_mock):
        """
        Chech if the create user service calls to the storage client persist method
        """
        mock_hash_pass = 'mocked_hash_pass'
        hash_mock.return_value = mock_hash_pass
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.user_service.create_user(TEST_USERNAME, TEST_PASSWORD))
        self.client_mock.save.assert_called_once()
        self.assertEqual(self.client_mock.save.call_args[0][0].username, TEST_USERNAME)
        self.assertEqual(self.client_mock.save.call_args[0][0].password, mock_hash_pass)

    def test_get_user_id(self):
        """
        Check if the get user by id method returns the stored instance
        """
        loop = asyncio.new_event_loop()
        self.client_mock.get_one.return_value = User(username=TEST_USERNAME, password=TEST_PASSWORD)
        result = loop.run_until_complete(self.user_service.get_user_by_id(1))
        self.assertEqual(result.username, TEST_USERNAME)

    def test_get_user_name(self):
        """
        Check if the get user by name method returns the stored instance
        """
        loop = asyncio.new_event_loop()
        self.client_mock.get_one.return_value = User(username=TEST_USERNAME, password=TEST_PASSWORD)
        result = loop.run_until_complete(self.user_service.get_user_by_name(TEST_USERNAME))
        self.assertEqual(result.username, TEST_USERNAME)
