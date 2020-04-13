"""
Celery tasks unit tests module
"""
import json
from unittest import TestCase
from unittest.mock import patch, MagicMock

from news_service_lib import NlpServiceService
from news_service_lib.models import New, NamedEntity

from nlp_service.nlp_celery_worker.celery_nlp_tasks import initialize_worker, hydrate_new_with_entities, \
    publish_hydrated_new


class TestCeleryTasks(TestCase):

    TEST_NEW = New(title='test_title', content='test_content', categories=['test_category'], date=123123.0)
    TEST_ENTITIES = [NamedEntity(text='test_entity_text', type='test_entity_type')]

    TEST_NLP_SERVICE_CONFIG = dict(protocol='test_protocol', host='test_host', port='0')
    TEST_QUEUE_CONFIG = dict(host='test_host', port='0', user='test_user', password='test_password')

    @patch('nlp_service.nlp_celery_worker.celery_nlp_tasks.NlpServiceService')
    @patch('nlp_service.nlp_celery_worker.celery_nlp_tasks.CELERY_APP')
    def test_initialize_worker(self, _, __):
        """
        Test initializing worker sets nlp service and queue_provider_config
        """
        initialize_worker(self.TEST_NLP_SERVICE_CONFIG, self.TEST_QUEUE_CONFIG)

        from nlp_service.nlp_celery_worker.celery_nlp_tasks import nlp_service_service
        self.assertIsNotNone(nlp_service_service)

        from nlp_service.nlp_celery_worker.celery_nlp_tasks import queue_provider_config
        self.assertEqual(queue_provider_config, self.TEST_QUEUE_CONFIG)

    @patch.object(NlpServiceService, 'get_entities')
    @patch('nlp_service.nlp_celery_worker.celery_nlp_tasks.CELERY_APP')
    def test_hydrate_entities(self, _, mocked_nlp_service):
        """
        Test hydrate new with entity set extracted entities in the input new
        """
        async def entities_response():
            return self.TEST_ENTITIES
        mocked_nlp_service.return_value = entities_response()
        initialize_worker(self.TEST_NLP_SERVICE_CONFIG, self.TEST_QUEUE_CONFIG)
        hydrated_new = hydrate_new_with_entities(dict(self.TEST_NEW))
        self.assertListEqual(hydrated_new['entities'], [dict(entity) for entity in self.TEST_ENTITIES])

    @patch('nlp_service.nlp_celery_worker.celery_nlp_tasks.PlainCredentials')
    @patch('nlp_service.nlp_celery_worker.celery_nlp_tasks.ConnectionParameters')
    @patch('nlp_service.nlp_celery_worker.celery_nlp_tasks.BlockingConnection')
    @patch('nlp_service.nlp_celery_worker.celery_nlp_tasks.NlpServiceService')
    @patch('nlp_service.nlp_celery_worker.celery_nlp_tasks.CELERY_APP')
    def test_publish_new(self, _, __, mocked_connection, ___, ____):
        """
        Test publishing new declares the exchange, publish the new, sets hydrated of new as true, closes the channel
        and closes the connection
        """
        initialize_worker(self.TEST_NLP_SERVICE_CONFIG, self.TEST_QUEUE_CONFIG)
        channel_mock = MagicMock()
        mocked_connection().channel.return_value = channel_mock
        publish_hydrated_new(dict(self.TEST_NEW))

        channel_mock.exchange_declare.assert_called_with(exchange='news', exchange_type='fanout', durable=True)
        self.TEST_NEW.hydrated = True
        channel_mock.basic_publish.assert_called_with(exchange='news', routing_key='', body=json.dumps(dict(self.TEST_NEW)))

        channel_mock.close.assert_called_once()
        mocked_connection().close.assert_called_once()
