"""
News service common middlewares
"""
from typing import Callable

from aiohttp.web_app import Application
from aiohttp.web_request import Request
from aiohttp.web_response import Response


async def uaa_auth_middleware(app: Application, handler: Callable):
    """
    This middlewares check if the requests are authenticated using the uaa service

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
