import json
from unittest import TestCase

from ..error_utils import json_error


class TestErrorUtils(TestCase):

    def test_json_error(self):
        test_exception_msg = 'Test exception'
        test_error_status = 12345
        error_response = json_error(test_error_status, Exception(test_exception_msg))
        error_response_data = json.loads(str(error_response.body, 'UTF-8'))
        self.assertEqual('Exception', error_response_data['error'])
        self.assertEqual(test_exception_msg, error_response_data['detail'])
        self.assertEqual(test_error_status, error_response.status)
