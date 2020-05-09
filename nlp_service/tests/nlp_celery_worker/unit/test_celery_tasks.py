"""
Celery tasks unit tests module
"""
import json
from unittest import TestCase
from unittest.mock import patch, MagicMock

from news_service_lib import NlpServiceService
from news_service_lib.models import New, NamedEntity, NLPDoc

from nlp_service.nlp_celery_worker import celery_nlp_tasks
from nlp_service.nlp_celery_worker.celery_nlp_tasks import initialize_worker, hydrate_new_with_entities, \
    publish_hydrated_new, process_content, hydrate_new_summary, hydrate_new_sentiment


class TestCeleryTasks(TestCase):

    TEST_NEW = New(title='test_title', content='test_content', source='test_source', date=123123.0)
    TEST_ENTITIES = [NamedEntity(text='test_entity_text', type='test_entity_type')]
    TEST_NAMED_ENTITIES = [('Test_ENTITY_text', 'test_entity_type'), ('Test_ENTITY_text', 'test_entity_type')]
    TEST_PROCESSED_TEXT = NLPDoc(sentences=['test_sentence_1', 'test_sentence_2'], named_entities=TEST_NAMED_ENTITIES)
    TEST_SUMMARY = 'Test summary'
    TEST_SENTIMENT = 0.4

    TEST_NLP_SERVICE_CONFIG = dict(protocol='test_protocol', host='test_host', port='0')
    TEST_QUEUE_CONFIG = dict(host='test_host', port='0', user='test_user', password='test_password')

    @patch.object(NlpServiceService, 'process_text')
    @patch('nlp_service.nlp_celery_worker.celery_nlp_tasks.CELERY_APP')
    def test_initialize_worker(self, _, mocked_nlp_service):
        """
        Test initializing worker sets nlp service and queue_provider_config
        """
        async def process_response():
            return self.TEST_PROCESSED_TEXT

        mocked_nlp_service.return_value = process_response()

        initialize_worker(self.TEST_NLP_SERVICE_CONFIG, self.TEST_QUEUE_CONFIG)

        from nlp_service.nlp_celery_worker.celery_nlp_tasks import NLP_REMOTE_SERVICE
        self.assertIsNotNone(NLP_REMOTE_SERVICE)

        from nlp_service.nlp_celery_worker.celery_nlp_tasks import QUEUE_PROVIDER_CONFIG
        self.assertEqual(QUEUE_PROVIDER_CONFIG, self.TEST_QUEUE_CONFIG)

    @patch.object(NlpServiceService, 'process_text')
    @patch('nlp_service.nlp_celery_worker.celery_nlp_tasks.CELERY_APP')
    def test_process_text(self, _, mocked_nlp_service):
        """
        Test process text outputs the input new and the processed text data
        """
        async def process_response():
            return self.TEST_PROCESSED_TEXT

        mocked_nlp_service.return_value = process_response()
        initialize_worker(self.TEST_NLP_SERVICE_CONFIG, self.TEST_QUEUE_CONFIG)
        new, nlp_doc = process_content(dict(self.TEST_NEW))
        self.assertEqual(new, dict(self.TEST_NEW))
        self.assertEqual(nlp_doc, dict(self.TEST_PROCESSED_TEXT))

    @patch('nlp_service.nlp_celery_worker.celery_nlp_tasks.CELERY_APP')
    def test_hydrate_new_entities(self, _):
        """
        Test hydrate with entities adds the named entities extracted removing duplicates and in lowercase
        """
        new, nlp_doc = hydrate_new_with_entities((dict(self.TEST_NEW), dict(self.TEST_PROCESSED_TEXT)))
        self.assertEqual(nlp_doc, dict(self.TEST_PROCESSED_TEXT))
        self.assertListEqual(new['entities'], [dict(entity) for entity in self.TEST_ENTITIES])

    @patch('nlp_service.nlp_celery_worker.celery_nlp_tasks.generate_summary_from_sentences')
    @patch('nlp_service.nlp_celery_worker.celery_nlp_tasks.CELERY_APP')
    def test_hydrate_new_summary(self, _, mocked_generate_summary):
        """
        Test hydrate with summary adds the generated content summary to the new
        """
        mocked_generate_summary.return_value = self.TEST_SUMMARY
        new, nlp_doc = hydrate_new_summary((dict(self.TEST_NEW), dict(self.TEST_PROCESSED_TEXT)))
        self.assertEqual(nlp_doc, dict(self.TEST_PROCESSED_TEXT))
        self.assertEqual(new['summary'], self.TEST_SUMMARY)

    @patch('nlp_service.nlp_celery_worker.celery_nlp_tasks.CELERY_APP')
    def test_hydrate_new_sentiment(self, _):
        """
        Test hydrate with sentiment adds the sentiment score of the content
        """
        sentiment_analyzer_mock = MagicMock()
        sentiment_analyzer_mock.return_value = self.TEST_SENTIMENT
        celery_nlp_tasks.SENTIMENT_ANALYZER = sentiment_analyzer_mock
        new = hydrate_new_sentiment((dict(self.TEST_NEW), dict(self.TEST_PROCESSED_TEXT)))
        self.assertEqual(new['sentiment'], self.TEST_SENTIMENT)

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
