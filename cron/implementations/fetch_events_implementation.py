"""
Fetch events cron module
"""
from aiohttp.web_app import Application

from cron.implementations.implementation import Implementation
from log_config import get_logger

LOGGER = get_logger()


class FetchEventsImplementation(Implementation):
    """
    Fetch events cron implementation
    """
    def __init__(self, app: Application, definition: dict):
        """
        Initialize the fetch events cron

        Args:
            app: application which runs the cron
            definition: fetch events cron definition parameters
        """
        Implementation.__init__(self, app, definition)

    def _run(self):
        """
        Fetch events functionality
        """
        LOGGER.info('Fetching events from %s', self.definition['event_source_url'])

        event_service = self.app['event_service']

        for adapter_class in self.definition['source_adapters']:
            adapter = adapter_class(self.definition)
            for event in adapter.fetch():
                event_service.save_event(event)
