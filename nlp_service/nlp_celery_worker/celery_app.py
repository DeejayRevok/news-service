"""
Main nlp celery worker module
"""
import sys

from celery import Celery
from news_service_lib import profile_args_parser, Configuration, ConfigProfile, add_logstash_handler

from nlp_service.log_config import LOG_CONFIG
from nlp_service.nlp_celery_worker.nlp_helpers.summarizer import initialize_summarizer
from nlp_service.webapp.definitions import CONFIG_PATH


class CeleryApp:
    """
    Celery worker application implementation
    """
    BASE_BROKER_URL = 'pyamqp://{user}:{password}@{host}:{port}//'
    TASK_IMPORTS = ['nlp_service.nlp_celery_worker.celery_nlp_tasks']

    def __init__(self):
        """
        Initialize the celery application
        """
        self.app = Celery('Nlp service worker', include=self.TASK_IMPORTS)

    def configure(self, broker_config: dict, worker_concurrency: int):
        """
        Configure the current celery application in order to set the broker service configuration
        and the worker concurrency number

        Args:
            broker_config: broker service configuration
            worker_concurrency: number of worker concurrent threads

        """
        broker_url = self.BASE_BROKER_URL.format(**broker_config)
        self.app.config_from_object(
            dict(broker_url=broker_url, result_backend='rpc://', worker_concurrency=worker_concurrency))

    def run(self):
        """
        Run the associated celery app

        Returns:

        """
        sys.argv = [sys.argv[0]]
        self.app.worker_main()


CELERY_APP = CeleryApp()

if __name__ == '__main__':
    ARGS = profile_args_parser('NLP Celery worker')

    initialize_summarizer()

    CONFIGURATION = Configuration(ConfigProfile[ARGS['profile']], CONFIG_PATH)
    add_logstash_handler(LOG_CONFIG, CONFIGURATION.get('LOGSTASH', 'host'), int(CONFIGURATION.get('LOGSTASH', 'port')))
    CELERY_APP.configure(CONFIGURATION.get_section('RABBIT'), int(CONFIGURATION.get('CELERY', 'concurrency')))
    CELERY_APP.run()
