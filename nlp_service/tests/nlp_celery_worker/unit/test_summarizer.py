from unittest import TestCase
from unittest.mock import patch

from nlp_service.nlp_celery_worker.nlp_helpers.summarizer import initialize_summarizer, generate_summary_from_sentences


class TestSummarizer(TestCase):
    TEST_INPUT_SENTENCES = ['Esta frase aporta significado.', 'De eso y esto y lo otro pero nada.',
                            'Una frase diferente pero con mucha importancia.',
                            'Esta frase aporta significado y significado.']

    OUTPUT_SUMMARY_SENTENCES = ['Una frase diferente pero con mucha importancia.',
                                'Esta frase aporta significado y significado.']
    OUTPUT_SUMMARY_EXCLUDED_SENTENCES = ['Esta frase aporta significado.', 'De eso y esto y lo otro pero nada.']

    @patch('nlp_service.nlp_celery_worker.nlp_helpers.summarizer.download')
    def test_initialize_summarizer(self, download_mock):
        initialize_summarizer()
        download_mock.assert_called_with('stopwords')

    def test_generate_summary_from_sentences(self):
        initialize_summarizer()
        summary = generate_summary_from_sentences(self.TEST_INPUT_SENTENCES, summary_sentences=2)
        for sentence in self.OUTPUT_SUMMARY_SENTENCES:
            self.assertIn(sentence, summary)
        for sentence in self.OUTPUT_SUMMARY_EXCLUDED_SENTENCES:
            self.assertNotIn(sentence, summary)
