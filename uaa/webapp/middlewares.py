"""
UAA webapp middlewares module
"""
from typing import Callable

from aiohttp.web_app import Application
from aiohttp.web_exceptions import HTTPException, HTTPUnauthorized
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from news_service_lib import json_error

from uaa.lib.jwt_tools import decode_token
from uaa.log_config import get_logger

LOGGER = get_logger()


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
            LOGGER.error('Request %s has failed with exception: %s', request, repr(ex), exc_info=True)
            app['apm'].client.end_transaction(f'{request.method}{request.rel_url}', 500)
            app['apm'].client.capture_exception()
            return json_error(500, ex)
    return middleware


async def auth_middleware(app: Application, handler: Callable) -> Callable:
    """
    Middleware used to verify the authentication JWT token

    Args:
        app: application associated
        handler: request handler

    Returns: authentication middleware

    """
    async def middleware(request: Request):
        request.user = None
        jwt_token = request.headers.getone('X-API-Key', None)
        if jwt_token:
            payload = decode_token(jwt_token)
            try:
                request.user = await app['user_service'].get_user_data(payload['user_id'])
            except KeyError:
                raise HTTPUnauthorized(reason='Wrong authorization token')
        return await handler(request)
    return middleware
