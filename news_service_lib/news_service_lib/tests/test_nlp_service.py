"""
NLP service test module
"""
from unittest import TestCase
from unittest.mock import patch

from aiohttp.web_exceptions import HTTPUnauthorized, HTTPInternalServerError
from aiounittest import async_test
from asynctest import patch as async_patch, CoroutineMock
from news_service_lib import NlpServiceService
from news_service_lib.models import New, NamedEntity, NLPDoc


class TestNLPService(TestCase):
    TEST_NEW = New(title='Test_title', content='Test_content', date=112341234.0, categories=['Test_category'])
    TEST_HOST = 'test_host'
    TEST_PORT = '0'
    TEST_PROTOCOL = 'test_protocol'
    TEST_ERROR_DETAIL = 'test_detail'
    TEST_NLP_DOC = NLPDoc(sentences=['test_sentence_1', 'test_sentence_2'],
                          named_entities=[('test_entity_text', 'test_entity_type')])

    @patch('news_service_lib.nlp_service_service.get_system_auth_token')
    @async_patch('aiohttp.ClientSession.put')
    @async_test
    async def test_hydrate_new_success(self, mock_put, mock_get_token):
        """
        Test hydrate new calls hydrate new endpoint with the new to hydrate
        """
        mock_get_token.return_value = 'TEST_SYSTEM_TOKEN'
        mock_put.return_value.__aenter__.return_value.status = 204
        nlp_service = NlpServiceService(self.TEST_PROTOCOL, self.TEST_HOST, self.TEST_PORT)
        await nlp_service.hydrate_new(self.TEST_NEW)
        mock_put.assert_called_with(
            f'{self.TEST_PROTOCOL}://{self.TEST_HOST}:{self.TEST_PORT}/{nlp_service.PATHS["hydrate_new"]}',
            data=dict(self.TEST_NEW))

    @patch('news_service_lib.nlp_service_service.get_system_auth_token')
    @async_patch('aiohttp.ClientSession.put')
    @async_test
    async def test_hydrate_new_unauthorized(self, mock_put, mock_get_token):
        """
        Test hydrate new unauthorized raises unauthorized error
        """
        mock_get_token.return_value = 'TEST_SYSTEM_TOKEN'
        mock_put.return_value.__aenter__.return_value.status = 401
        mock_put.return_value.__aenter__.return_value.json = CoroutineMock(
            side_effect=[dict(detail=self.TEST_ERROR_DETAIL)])
        nlp_service = NlpServiceService(self.TEST_PROTOCOL, self.TEST_HOST, self.TEST_PORT)
        try:
            await nlp_service.hydrate_new(self.TEST_NEW)
            self.fail()
        except HTTPUnauthorized as unex:
            self.assertEqual(unex.reason, self.TEST_ERROR_DETAIL)

    @patch('news_service_lib.nlp_service_service.get_system_auth_token')
    @async_patch('aiohttp.ClientSession.put')
    @async_test
    async def test_hydrate_new_fail(self, mock_put, mock_get_token):
        """
        Test hydrate new request failed raises internal server error
        """
        mock_get_token.return_value = 'TEST_SYSTEM_TOKEN'
        mock_put.return_value.__aenter__.return_value.status = 500
        mock_put.return_value.__aenter__.return_value.json = CoroutineMock(
            side_effect=[dict(detail=self.TEST_ERROR_DETAIL)])
        nlp_service = NlpServiceService(self.TEST_PROTOCOL, self.TEST_HOST, self.TEST_PORT)
        try:
            await nlp_service.hydrate_new(self.TEST_NEW)
            self.fail()
        except HTTPInternalServerError as unex:
            self.assertEqual(unex.reason, self.TEST_ERROR_DETAIL)

    @patch('news_service_lib.nlp_service_service.get_system_auth_token')
    @async_patch('aiohttp.ClientSession.put')
    @async_test
    async def test_hydrate_new_call_fail(self, mock_put, mock_get_token):
        """
        Test hydrate new method call fail raises connection error
        """
        mock_get_token.return_value = 'TEST_SYSTEM_TOKEN'
        mock_put.side_effect = Exception('Test')
        nlp_service = NlpServiceService(self.TEST_PROTOCOL, self.TEST_HOST, self.TEST_PORT)
        with self.assertRaises(ConnectionError):
            await nlp_service.hydrate_new(self.TEST_NEW)

    @patch('news_service_lib.nlp_service_service.get_system_auth_token')
    @async_patch('aiohttp.ClientSession.post')
    @async_test
    async def test_process_text_success(self, mock_post, mock_get_token):
        """
        Test get entities success returns the named entities calling to the get entities endpoint
        """
        mock_get_token.return_value = 'TEST_SYSTEM_TOKEN'
        mock_post.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.json = CoroutineMock(
            side_effect=[dict(self.TEST_NLP_DOC)])
        nlp_service = NlpServiceService(self.TEST_PROTOCOL, self.TEST_HOST, self.TEST_PORT)
        nlp_doc = await nlp_service.process_text(self.TEST_NEW.content)
        mock_post.assert_called_with(
            f'{self.TEST_PROTOCOL}://{self.TEST_HOST}:{self.TEST_PORT}/{nlp_service.PATHS["process_text"]}',
            data=dict(text=self.TEST_NEW.content))
        self.assertEqual(nlp_doc, self.TEST_NLP_DOC)

    @patch('news_service_lib.nlp_service_service.get_system_auth_token')
    @async_patch('aiohttp.ClientSession.post')
    @async_test
    async def test_get_entities_unauthorized(self, mock_post, mock_get_token):
        """
        Test the get entities unauthorized raises unauthorized http error
        """
        mock_get_token.return_value = 'TEST_SYSTEM_TOKEN'
        mock_post.return_value.__aenter__.return_value.status = 401
        mock_post.return_value.__aenter__.return_value.json = CoroutineMock(
            side_effect=[dict(detail=self.TEST_ERROR_DETAIL)])
        nlp_service = NlpServiceService(self.TEST_PROTOCOL, self.TEST_HOST, self.TEST_PORT)
        try:
            await nlp_service.process_text(self.TEST_NEW.content)
            self.fail()
        except HTTPUnauthorized as unex:
            self.assertEqual(unex.reason, self.TEST_ERROR_DETAIL)

    @patch('news_service_lib.nlp_service_service.get_system_auth_token')
    @async_patch('aiohttp.ClientSession.post')
    @async_test
    async def test_get_entities_fail(self, mock_post, mock_get_token):
        """
        Test get entities request fail raises internal server error
        """
        mock_get_token.return_value = 'TEST_SYSTEM_TOKEN'
        mock_post.return_value.__aenter__.return_value.status = 500
        mock_post.return_value.__aenter__.return_value.json = CoroutineMock(
            side_effect=[dict(detail=self.TEST_ERROR_DETAIL)])
        nlp_service = NlpServiceService(self.TEST_PROTOCOL, self.TEST_HOST, self.TEST_PORT)
        try:
            await nlp_service.process_text(self.TEST_NEW.content)
            self.fail()
        except HTTPInternalServerError as unex:
            self.assertEqual(unex.reason, self.TEST_ERROR_DETAIL)

    @patch('news_service_lib.nlp_service_service.get_system_auth_token')
    @async_patch('aiohttp.ClientSession.post')
    @async_test
    async def test_get_entities_call_fail(self, mock_post, mock_get_token):
        """
        Test get entities method call failed raises connection error
        """
        mock_get_token.return_value = 'TEST_SYSTEM_TOKEN'
        mock_post.side_effect = Exception('Test')
        nlp_service = NlpServiceService(self.TEST_PROTOCOL, self.TEST_HOST, self.TEST_PORT)
        with self.assertRaises(ConnectionError):
            await nlp_service.process_text(self.TEST_NEW.content)
