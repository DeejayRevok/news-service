"""
Cron factory
Run all the defined crons in the cron definitions module
"""
from typing import Optional

from aiohttp.web_app import Application

from cron.cron_definitions import DEFINITIONS


def initialize_crons(app: Optional[Application]):
    """
    Initialize the crons defined

    Args:
        app: application which runs the crons
    """
    for definition in DEFINITIONS.values():
        definition['class'](app, definition)
