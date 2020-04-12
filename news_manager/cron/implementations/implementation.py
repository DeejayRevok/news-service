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

        @crontab(definition['expression'])
        async def scheduled():
            """
            Cron scheduled runner
            """
            self.app['apm'].client.begin_transaction('cron_execution')
            await self._run()
            self.app['apm'].client.end_transaction(f'{self.definition["class"].__name__}', 'OK')

        scheduled.start()

    @abstractmethod
    async def _run(self):
        """
        Specific cron functionality
        """
