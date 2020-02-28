import unittest
from os.path import join, dirname
from unittest.mock import patch
from xml.etree.ElementTree import Element, fromstring

from adapters.xml_event_endpoint_adapter import XmlEventEndpointAdapter


def adapt_pass(value):
    return list(value)


class MockedResponse:

    def __init__(self, content):
        self.content = content


class TestXmlAdapter(unittest.TestCase):

    XML_RESPONSE_PATH = join(dirname(dirname(__file__)), 'resources', 'event_response.xml')

    def setUp(self):
        """
        Set up the environment for testing reading the xml response file
        """
        with open(self.XML_RESPONSE_PATH, 'r') as xml_response_file:
            self.mocked_xml_response = MockedResponse(xml_response_file.read())
            self.mocked_elements = []
            event_list = fromstring(self.mocked_xml_response.content)
            for item in event_list:
                for event in item:
                    if event.tag == XmlEventEndpointAdapter.ROOT_XML_TAG:
                        self.mocked_elements.append(event)

    @patch('requests.get')
    def test_fetch(self, requests_get):
        """
        Test fetching events return events
        """
        requests_get.return_value = self.mocked_xml_response
        xml_event_adapter = XmlEventEndpointAdapter({'event_source_url': None})
        xml_event_adapter.adapt = adapt_pass
        fetch_return = xml_event_adapter.fetch()
        assert len(fetch_return) == 3
        for elem in fetch_return:
            assert isinstance(elem, Element)

    def test_adapt(self):
        """
        Test adapt events returns parsed events
        """
        xml_event_adapter = XmlEventEndpointAdapter({'event_source_url': None})
        adapt_return = list(xml_event_adapter.adapt(self.mocked_elements))
        assert len(adapt_return) == 3
        for adapted_elem in adapt_return:
            assert isinstance(adapted_elem, dict)
            assert isinstance(adapted_elem['base_event']['event']['event_date'], float)
            assert isinstance(adapted_elem['base_event']['event']['sell_from'], float)
            assert isinstance(adapted_elem['base_event']['event']['sell_to'], float)


if __name__ == '__main__':
    unittest.main()
