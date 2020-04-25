"""
El confidencial rss adapter module
"""
from time import mktime, strptime
from typing import Iterator
from xml.etree.ElementTree import Element, fromstring, tostring

import requests
from bs4 import BeautifulSoup
from lxml import html
from news_service_lib.models import New
from xmltodict import parse

from news_manager.adapters.source_adapter import SourceAdapter
from news_manager.log_config import get_logger

LOGGER = get_logger()


class ConfidencialRssNewsAdapter(SourceAdapter):
    """
    El confidencial rss news adapter
    """
    DATE_INPUT_FORMAT = '%a, %d %b %Y %H:%M:%S %z'
    ROOT_NEW_TAG = '{http://www.w3.org/2005/Atom}entry'

    def _fetch(self) -> Iterator[Element]:
        """
        Fetch news from the 'El confidencial' rss

        Returns: 'El confidencial' rss fetched items parsed

        """
        LOGGER.info('Fetching news from %s', self.source_params['el_confidencial_rss'])
        response = requests.get(self.source_params['el_confidencial_rss'])
        rss = fromstring(response.content)
        for item in rss:
            if item.tag == self.ROOT_NEW_TAG:
                yield item

    def _adapt_single(self, item: Element) -> New:
        """
        Convert a single fetched xml parsed item

        Args:
            item: parsed xml item

        Returns: new representation of the item

        """
        new_dict = parse(tostring(item).decode(), attr_prefix='')['ns0:entry']
        LOGGER.info('Found new with title %s', new_dict['ns0:title'])

        content = self._parse_content(new_dict['ns0:content']['#text'])

        date = mktime(strptime(new_dict['ns0:published'], '%Y-%m-%dT%H:%M:%S%z'))

        return New(title=new_dict['ns0:title'], content=content, source='El Confidencial', date=date)

    def _parse_content(self, html_string: str) -> str:
        """
        Parse the html content into string

        Args:
            html_string: input html string to parse

        Returns: text of the input html

        """
        if html.fromstring(html_string).find('.//*') is not None:
            html_content = BeautifulSoup(html_string, 'html.parser').text
            return self._parse_content(html_content)
        else:
            return html_string
