"""
El confidencial adapter tests module
"""
from os.path import join, dirname
from unittest import TestCase
from unittest.mock import patch
from xml.etree.ElementTree import fromstring, Element

from news_service_lib.models import New

from news_manager.adapters.elconfidencial_rss_news_adapter import ConfidencialRssNewsAdapter


def adapt_pass(value):
    """
    Mocked helper function on adapt
    """
    return list(value)


class MockedResponse:
    """
    Mocked response helper function
    """
    def __init__(self, content):
        self.content = content


class TestElConfidencialAdapter(TestCase):
    """
    El confidencial adapter test cases implementation
    """
    XML_RESPONSE_PATH = join(dirname(dirname(__file__)), 'resources', 'el_confidencial_news_response.xml')

    def setUp(self):
        """
        Set up the environment for testing reading the xml response file
        """
        with open(self.XML_RESPONSE_PATH, 'r') as xml_response_file:
            self.mocked_xml_response = MockedResponse(xml_response_file.read())
            self.mocked_elements = []
            rss = fromstring(self.mocked_xml_response.content)
            for item in rss:
                if item.tag == ConfidencialRssNewsAdapter.ROOT_NEW_TAG:
                    self.mocked_elements.append(item)

    @patch('requests.get')
    def test_fetch(self, requests_get):
        """
        Test fetching elements from rss return xml elements
        """
        requests_get.return_value = self.mocked_xml_response
        xml_rss_adapter = ConfidencialRssNewsAdapter({'el_confidencial_rss': None})
        xml_rss_adapter.adapt = adapt_pass
        fetch_return = list(xml_rss_adapter._fetch())
        self.assertEqual(len(fetch_return), 2)
        for elem in fetch_return:
            self.assertTrue(isinstance(elem, Element))

    def test_adapt(self):
        """
        Test adapt news returns parsed news
        """
        xml_rss_adapter = ConfidencialRssNewsAdapter({'abc_rss': None})
        adapt_return = list(xml_rss_adapter.adapt(self.mocked_elements))
        self.assertEqual(len(adapt_return), 2)
        for adapted_elem in adapt_return:
            self.assertTrue(isinstance(adapted_elem, New))
