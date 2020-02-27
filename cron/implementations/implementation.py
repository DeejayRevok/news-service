"""
Generic cron runner and interface module
"""
from abc import abstractmethod

from aiocron import crontab
from aiohttp.web_app import Application


class Implementation:
    """
    Generic cron runner implementation
    """
    def __init__(self, app: Application, definition: dict):
        """
        Initialize the cron runner

        Args:
            app: application which runs the cron
            definition: specific cron definition params
        """
        self.app = app
        self.definition = definition
        self._run()

        @crontab(definition['expression'])
        async def scheduled():
            """
            Cron scheduled runner
            """
            self._run()

        scheduled.start()

    @abstractmethod
    def _run(self):
        """
        Specific cron functionality
        """
