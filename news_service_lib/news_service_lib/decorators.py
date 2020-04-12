"""
Decorators for news service module
"""
from typing import Callable

from aiohttp.web_exceptions import HTTPUnauthorized
from aiohttp.web_request import Request


def login_required(func: Callable):
    """
    Decorator used to check if the request is authenticated

    Args:
        func: function to decorate

    Returns: decorated function checking the authentication

    """
    def wrapper(request: Request):
        if not request.user:
            raise HTTPUnauthorized(reason='User is not present')
        return func(request)
    return wrapper
