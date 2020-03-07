"""
aiohttp middlewares module
"""
from typing import Callable

from aiohttp.web_app import Application
from aiohttp.web_exceptions import HTTPException
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from requests import Response

from event_manager.log_config import get_logger

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


async def error_middleware(app: Application, handler: Callable):
    """
    This middleware handles exceptions received from views or previous middleware.

    Args:
        app: web application
        handler: request handler

    Returns: error middleware

    """

    async def middleware(request: Request) -> Response:
        try:
            app['apm'].client.begin_transaction('request')
            response = await handler(request)
            app['apm'].client.end_transaction(f'{request.method}{request.rel_url}', response.status)
            return response
        except HTTPException as ex:
            LOGGER.error('Request %s has failed with exception: %s', request, repr(ex))
            app['apm'].client.end_transaction(f'{request.method}{request.rel_url}', ex.status)
            app['apm'].client.capture_exception()
            return json_error(ex.status, ex)
        except Exception as ex:
            LOGGER.error('Request %s has failed with exception: %s', request, repr(ex))
            app['apm'].client.end_transaction(f'{request.method}{request.rel_url}', 500)
            app['apm'].client.capture_exception()
            return json_error(500, ex)

    return middleware


async def auth_middleware(app: Application, handler: Callable):
    """
    This middlewares check if the requests are authenticated

    Args:
        app: web application
        handler: request handler

    Returns: authentication middleware

    """
    async def middleware(request: Request) -> Response:
        request.user = None
        jwt_token = request.headers.get('X-API-Key', None)
        if jwt_token:
            request.user = await app['uaa_service'].validate_token(jwt_token)
        return await handler(request)
    return middleware
