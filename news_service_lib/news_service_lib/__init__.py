"""
News service library declarations module
"""
from .config import ConfigProfile, Configuration
from .server_utils import initialize_server, finish_server_startup, server_runner, profile_args_parser, initialize_apm
from .aio_class_route_table import ClassRouteTableDef
from .apispec_utils import setup_aiohttp_apispec_mod, AiohttpApiSpecMod
from .error_utils import json_error
from .healthcheck import HealthCheck
from .log_utils import add_logstash_handler, get_base_log_config
from .jwt_tools import generate_token, decode_token
from .uaa_service import get_uaa_service, get_system_auth_token
from .middlewares import uaa_auth_middleware
from .decorators import login_required
from .nlp_service_service import NlpServiceService

__all__ = [
    "ConfigProfile",
    "Configuration",
    "initialize_server",
    "finish_server_startup",
    "server_runner",
    "initialize_apm",
    "profile_args_parser",
    "ClassRouteTableDef",
    "setup_aiohttp_apispec_mod",
    "AiohttpApiSpecMod",
    "json_error",
    "HealthCheck",
    "get_base_log_config",
    "add_logstash_handler",
    "generate_token",
    "decode_token",
    "get_uaa_service",
    "get_system_auth_token",
    "uaa_auth_middleware",
    "login_required",
    "NlpServiceService"
]
