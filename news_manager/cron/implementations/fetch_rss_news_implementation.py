"""
Fetch news cron module
"""
from aiohttp.web_app import Application

from news_manager.cron.implementations.implementation import Implementation
from news_manager.log_config import get_logger

LOGGER = get_logger()


class FetchRssNewsImplementation(Implementation):
    """
    Fetch news from rss cron implementation
    """
    def __init__(self, app: Application, definition: dict):
        """
        Initialize the fetch news cron

        Args:
            app: application which runs the cron
            definition: fetch news cron definition parameters
        """
        Implementation.__init__(self, app, definition)

    async def _run(self):
        """
        Fetch news from rss functionality
        """

        news_service = self.app['news_service']

        for adapter_class in self.definition['source_adapters']:
            adapter = adapter_class(self.definition)
            for new in adapter.fetch():
                await news_service.save_new(new)
