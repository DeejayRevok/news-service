"""
Custom date time tests module
"""
import datetime
from unittest import TestCase

from graphql.language.ast import StringValue

from news_manager.webapp.graph.utils.custom_date_time import CustomDateTime


class TestCustomDateTime(TestCase):
    """
    Custom date time tests cases implementation
    """
    def test_serialize(self):
        """
        Test serializing a string returns the string.
        Test serializing a datetime object returns the serialized date.
        """
        self.assertEqual('serialized', CustomDateTime.serialize('serialized'))

        date = datetime.datetime(year=2020, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        self.assertEqual('2020-01-01T00:00:00', CustomDateTime.serialize(date))

    def test_parse_literal(self):
        """
        Test parse literal parses the input graphQL string into a datetime object with the correct values
        """
        parsed = CustomDateTime.parse_literal(StringValue('2020-01-01T00:00:00'))
        self.assertIsInstance(parsed, datetime.datetime)
        self.assertEqual(parsed.year, 2020)

    def test_parse_value(self):
        """
        Test parse value parses the input string into a datetime object with the correct values
        """
        parsed = CustomDateTime.parse_value('2020-01-01T00:00:00')
        self.assertIsInstance(parsed, datetime.datetime)
        self.assertEqual(parsed.year, 2020)

