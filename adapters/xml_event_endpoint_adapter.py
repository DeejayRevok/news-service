"""
Adapter to xml endpoint source
"""
from time import strptime, mktime
from typing import Iterator
from xml.etree.ElementTree import fromstring, tostring, Element

import requests
from xmltodict import parse

from adapters.source_adapter import SourceAdapter
from log_config import get_logger

LOGGER = get_logger()


class XmlEventEndpointAdapter(SourceAdapter):
    """
    xml endpoint source adapter implementation
    """
    DATE_INPUT_FORMAT = '%Y-%m-%dT%H:%M:%S'
    ROOT_XML_TAG = 'base_event'

    def _fetch(self) -> Iterator[Element]:
        """
        Fetch items from the xml endpoint

        Returns: xml endpoint fetched items parsed

        """
        response = requests.get(self.source_params['event_source_url'])
        event_list = fromstring(response.content)
        for item in event_list:
            for event in item:
                if event.tag == self.ROOT_XML_TAG:
                    LOGGER.info('Found new event of type %s with id %s', event.attrib['title'],
                                event.attrib['base_event_id'])
                    yield event

    def _adapt_single(self, item: Element) -> dict:
        """
        Convert a single fetched xml parsed item

        Args:
            item: parsed xml item

        Returns: xml item dict representation

        """
        event_dict = parse(tostring(item).decode(), attr_prefix='')
        event_dict[self.ROOT_XML_TAG]['event']['event_date'] = mktime(strptime(
            event_dict[self.ROOT_XML_TAG]['event']['event_date'],
            self.DATE_INPUT_FORMAT))
        event_dict[self.ROOT_XML_TAG]['event']['sell_from'] = mktime(strptime(
            event_dict[self.ROOT_XML_TAG]['event']['sell_from'],
            self.DATE_INPUT_FORMAT))
        event_dict[self.ROOT_XML_TAG]['event']['sell_to'] = mktime(
            strptime(event_dict[self.ROOT_XML_TAG]['event']['sell_to'],
                     self.DATE_INPUT_FORMAT))
        return event_dict
