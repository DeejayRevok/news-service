"""
GraphQL authentication utilities
"""
from typing import Callable

from aiohttp.web_exceptions import HTTPUnauthorized
from graphql import ResolveInfo


def login_required(func: Callable):
    """
    Decorator used to check if the request is authenticated

    Args:
        func: function to decorate

    Returns: decorated function checking the authentication

    """
    def wrapper(*args, **kwargs):
        graphql_info = None
        for arg in args:
            if isinstance(arg, ResolveInfo):
                graphql_info = arg
                break
        if not graphql_info:
            raise ValueError('GraphQL resolve info not found')
        request = graphql_info.context['request']
        if not request.user:
            raise HTTPUnauthorized(reason='User is not present')
        return func(*args, **kwargs)
    return wrapper
