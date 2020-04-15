"""
JWT Tools tests module
"""
import os
from unittest import TestCase

from ..jwt_tools import generate_token, decode_token


class TestJWTTools(TestCase):

    def setUp(self) -> None:
        """
        Clean the environment variables before test execution
        """
        if 'JWT_SECRET' in os.environ:
            os.environ.pop('JWT_SECRET')

    def test_generate_token_without_secret(self):
        """
        Test generating a token without secret specified raises Error
        """
        with self.assertRaises(ValueError):
            generate_token(dict(test='test'))

    def test_encode_decode_token_successfully(self):
        """
        Test the encode and decode of a valid token works
        """
        os.environ.update(dict(JWT_SECRET='test'))
        test_payload = dict(test='test')
        token = generate_token(test_payload)
        self.assertIsNotNone(token)
        decoded_payload = decode_token('Bearer ' + str(token, 'UTF-8'))
        self.assertEqual(decoded_payload, test_payload)

    def test_decode_token_malformed(self):
        """
        Test decoding token malformed raises error
        """
        with self.assertRaises(ValueError):
            decode_token('Test')

    def test_decode_token_without_secret(self):
        """
        Test decoding a token without secret specified raises error
        """
        with self.assertRaises(ValueError):
            decode_token('Bearer test')

    def test_decode_token_invalid(self):
        """
        Test decoding an invalid token raises error
        """
        os.environ.update(dict(JWT_SECRET='test'))
        with self.assertRaises(ValueError):
            decode_token('Bearer test')
