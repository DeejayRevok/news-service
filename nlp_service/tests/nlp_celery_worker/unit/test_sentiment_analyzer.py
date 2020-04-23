"""
Sentiment analyzer tests module
"""
from unittest import TestCase
from unittest.mock import patch

from nlp_service.nlp_celery_worker.nlp_helpers.sentiment_analyzer import initialize_sentiment_analyzer, \
    compute_overall_sentiment_sentences


class TestSentimentAnalyzer(TestCase):

    TEST_NEGATIVE_SENTENCES = ['Esta frase es algo buena', 'Esta frase es mala', 'Esta frase es muy negativa']
    TEST_POSITIVE_SENTENCES = ['Esta frase es algo mala', 'Esta frase es buena', 'Esta frase es muy buena']

    @patch('nlp_service.nlp_celery_worker.nlp_helpers.sentiment_analyzer.download')
    def test_initialize_sentiment_analyzer(self, download_mock):
        """
        Test initialize sentiment analyzer downloads the required resources
        """
        initialize_sentiment_analyzer()
        download_mock.assert_called_with('vader_lexicon')

    def test_negative_sentiment(self):
        """
        Test the sentiment analyzer with overall negative sentences returns negative score
        """
        initialize_sentiment_analyzer()
        sentiment_score = compute_overall_sentiment_sentences(self.TEST_NEGATIVE_SENTENCES)
        self.assertLess(sentiment_score, 0)

    def test_positive_sentiment(self):
        """
        Test the sentiment analyzer with overall positive sentences returns positive score
        """
        initialize_sentiment_analyzer()
        sentiment_score = compute_overall_sentiment_sentences(self.TEST_POSITIVE_SENTENCES)
        self.assertGreater(sentiment_score, 0)



