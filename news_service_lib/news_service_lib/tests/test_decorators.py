"""
Decorators test module
"""
from unittest import TestCase

from aiohttp.web_exceptions import HTTPUnauthorized
from news_service_lib import login_required


@login_required
def dummy_handler(request):
    """
    Dummy handler for testing
    """
    return request.user


class DummyRequest:
    """
    Dummy request for testing
    """
    def __init__(self, user):
        self.user = user


class TestDecorators(TestCase):
    """
    Decorator methods test case
    """
    TEST_REQUEST_USER = 'TEST'

    def test_login_required_user_provided(self):
        """
        Test when user is provided the login required decorator returns the result of the decorated function
        """
        mock_request = DummyRequest(self.TEST_REQUEST_USER)
        return_value = dummy_handler(mock_request)
        self.assertEqual(return_value, self.TEST_REQUEST_USER)

    def test_login_required_user_not_provided(self):
        """
        Test whe user is not provided the login required decorator raises unauthorized
        """
        mock_request = DummyRequest(None)
        with self.assertRaises(HTTPUnauthorized):
            dummy_handler(mock_request)
