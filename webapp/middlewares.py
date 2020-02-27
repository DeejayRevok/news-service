"""
aiohttp middlewares module
"""
from typing import Callable

from aiohttp.web_app import Application
from aiohttp.web_exceptions import HTTPException
from aiohttp.web_response import json_response
from requests import Response

from log_config import get_logger

LOGGER = get_logger()


def json_error(status_code: int, exception: Exception) -> Response:
    """
    Returns a Json Response from an exception.

    Args:
        status_code: response code
        exception: exception thrown

    Returns: web error json response

    """
    return json_response(data=dict(error=exception.__class__.__name__, detail=str(exception)),
                         status=status_code)


async def middleware_factory(_: Application, handler: Callable):
    """
    This middleware handles exceptions received from views or previous middleware.

    Args:
        _: web application
        handler: request handler

    Returns: error middleware

    """

    async def error_middleware(request) -> Response:
        try:
            response = await handler(request)
            return response
        except HTTPException as ex:
            LOGGER.error('Request %s has failed with exception: %s', request, repr(ex))
            return json_error(ex.status, ex)
        except Exception as ex:
            LOGGER.error('Request %s has failed with exception: %s', request, repr(ex))
            return json_error(500, ex)
    return error_middleware
