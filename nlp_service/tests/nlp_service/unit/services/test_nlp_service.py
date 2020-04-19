"""
NLP service tests module
"""
from unittest import TestCase
from unittest.mock import patch, MagicMock

from aiounittest import async_test
from news_service_lib.models import New

from nlp_service.services.nlp_service import NlpService


class TestNlpService(TestCase):
    """
    NLP service test cases implementation
    """
    TEST_NEW = New(title='test_title', content='test_content', date=2124124.0, categories=['test_category'])
    TEST_TEXT = 'test_text'
    TEST_ENTITY = ('test_entity_text', 'test_entity_type')
    TEST_SENTENCES = ['test_sentence_1', 'test_sentence_2']

    @patch('nlp_service.services.nlp_service.Pipeline')
    @async_test
    async def test_process_text(self, mocked_nlp_pipeline):
        """
        Test process text returns the NLP processed doc with the sentences and the named entities extracted from
        the text
        """
        mock_first_sentence = MagicMock()
        mock_first_sentence.text = self.TEST_SENTENCES[0]
        mock_second_sentence = MagicMock()
        mock_second_sentence.text = self.TEST_SENTENCES[1]

        mock_entity = MagicMock()
        mock_entity.text = self.TEST_ENTITY[0]
        mock_entity.type = self.TEST_ENTITY[1]

        nlp_service = NlpService()
        mocked_nlp_pipeline()().entities = [mock_entity]
        mocked_nlp_pipeline()().sentences = [mock_first_sentence, mock_second_sentence]
        nlp_doc = await nlp_service.get_processed_text(self.TEST_TEXT)
        mocked_nlp_pipeline().assert_called_with(self.TEST_TEXT)
        self.assertListEqual(nlp_doc.named_entities, [self.TEST_ENTITY])
        self.assertListEqual(nlp_doc.sentences, self.TEST_SENTENCES)

    @patch('nlp_service.services.nlp_service.publish_hydrated_new')
    @patch('nlp_service.services.nlp_service.hydrate_new_with_entities')
    @patch('nlp_service.services.nlp_service.Pipeline')
    @async_test
    async def test_hydrate_new(self, _, mocked_hydrate_new_entities, __):
        """
        Test hydrate new builds a chain linking all the specified tasks one behind another and calls the chain
        """
        hydrate_task_mock = MagicMock()
        NlpService.CELERY_NLP_PIPELINE = [mocked_hydrate_new_entities, hydrate_task_mock]
        mock_chain = MagicMock()
        mocked_hydrate_new_entities.s.return_value = mock_chain
        nlp_service = NlpService()
        await nlp_service.hydrate_new(dict(self.TEST_NEW))
        nlp_service.CELERY_NLP_PIPELINE[0].s.assert_called_with(dict(self.TEST_NEW))
        for task_mock in nlp_service.CELERY_NLP_PIPELINE[1:]:
            task_mock.s().link.assert_called_once()
        mock_chain.link.assert_called_with(hydrate_task_mock.s())
        mock_chain.delay.assert_called_once()