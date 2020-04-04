"""
News service error utils module
"""
from aiohttp.web_response import json_response, Response


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
