"""
Aiohttp application generic healthcheck module
"""
from typing import Callable

from aio_tiny_healthcheck import Checker
from aiohttp.web_app import Application


class HealthCheck:
    """
    Healthcheck wrapper implementation
    """
    def __init__(self, app: Application, callback: Callable):
        """
        Initialize the healtcheck for the specified application with the specified health check method

        Args:
            app: application to check health
            callback: health check implementation
        """
        self.app = app
        self.checker = callback
        healthcheck_provider = Checker(success_code=200, fail_code=500)
        healthcheck_provider.add_check('health_check', self.health_check)
        app.router.add_get('/healthcheck', healthcheck_provider.aiohttp_handler)

    async def health_check(self) -> True:
        """
        Perform the health check

        Returns: application health status

        """
        return await self.checker(self.app)
