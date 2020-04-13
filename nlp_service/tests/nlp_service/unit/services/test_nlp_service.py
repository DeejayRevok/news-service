from unittest import TestCase
from unittest.mock import patch, MagicMock, call

from aiounittest import async_test
from news_service_lib.models import NamedEntity, New

from nlp_service.services.nlp_service import NlpService


class TestNlpService(TestCase):

    TEST_NEW = New(title='test_title', content='test_content', date=2124124.0, categories=['test_category'])
    TEST_TEXT = 'test_text'
    TEST_ENTITIES = [NamedEntity(text='test_entity_text', type='test_entity_type')]

    @patch('nlp_service.services.nlp_service.Pipeline')
    @async_test
    async def test_get_named_entities(self, mocked_nlp_pipeline):
        nlp_service = NlpService()
        mocked_nlp_pipeline()().entities = self.TEST_ENTITIES
        entities = list(await nlp_service.get_named_entities(self.TEST_TEXT))
        mocked_nlp_pipeline().assert_called_with(self.TEST_TEXT)
        self.assertEqual(len(entities), 1)

    @patch('nlp_service.services.nlp_service.publish_hydrated_new')
    @patch('nlp_service.services.nlp_service.hydrate_new_with_entities')
    @patch('nlp_service.services.nlp_service.Pipeline')
    @async_test
    async def test_hydrate_new(self, _, mocked_hydrate_new_entities, mock_publish_task):
        hydrate_task_mock = MagicMock()
        NlpService.CELERY_NLP_PIPELINE = [mocked_hydrate_new_entities, hydrate_task_mock]
        mock_chain = MagicMock()
        mocked_hydrate_new_entities.s.return_value = mock_chain
        nlp_service = NlpService()
        await nlp_service.hydrate_new(dict(self.TEST_NEW))
        nlp_service.CELERY_NLP_PIPELINE[0].s.assert_called_with(dict(self.TEST_NEW))
        for task_mock in nlp_service.CELERY_NLP_PIPELINE[1:]:
            self.assertIn(call(task_mock.s()), mock_chain.link.mock_calls)
        mock_chain.link.assert_called_with(mock_publish_task.s())
        mock_chain.delay.assert_called_once()