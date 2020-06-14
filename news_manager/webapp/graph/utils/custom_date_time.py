"""
Custom date time scalar definition for graphql module
"""
import datetime
from typing import Any

from graphene.types import Scalar
from graphql.language import ast
from graphql.language.ast import Value, Node

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'


class CustomDateTime(Scalar):
    """
    Custom date time scalar implementation
    """
    @staticmethod
    def serialize(dt: Any) -> str:
        """
        Serialize the input date time like object

        Args:
            dt: input date time representation

        Returns: date time string representation

        """
        if not isinstance(dt, str):
            return dt.isoformat()
        else:
            return dt

    @staticmethod
    def parse_literal(node: Node) -> datetime:
        """
        Parse a string date time node to a datetime object

        Args:
            node: node to parse date time

        Returns: parsed date time

        """
        if isinstance(node, ast.StringValue):
            return datetime.datetime.strptime(
                node.value, DATE_FORMAT)

    @staticmethod
    def parse_value(value: str) -> datetime:
        """
        Parse a string date time representation

        Args:
            value: value to parse

        Returns: parsed date time string

        """
        return datetime.datetime.strptime(value, DATE_FORMAT)
