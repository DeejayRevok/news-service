"""
Sentiment analyzer tests module
"""
from unittest import TestCase
from unittest.mock import patch

from nlp_service.nlp_celery_worker.nlp_helpers.sentiment_analyzer import initialize_sentiment_analyzer, \
    SentimentAnalyzer


class TestSentimentAnalyzer(TestCase):

    TEST_NEGATIVE_SENTENCES = ['Esta frase es algo buena', 'Esta frase es mala', 'Esta frase es muy negativa']
    TEST_POSITIVE_SENTENCES = ['Esta frase es algo mala', 'Esta frase es buena', 'Esta frase es muy buena']
    TEST_POSITIVE_NEGATED_SENTENCE = ['Esta frase no es buena']
    TEST_NEGATIVE_NEGATED_SENTENCE = ['Esta frase no es mala']

    @patch('nlp_service.nlp_celery_worker.nlp_helpers.sentiment_analyzer.download')
    def test_initialize_sentiment_analyzer(self, download_mock):
        """
        Test initialize sentiment analyzer downloads the required resources
        """
        initialize_sentiment_analyzer()
        download_mock.assert_called_with('es_core_news_sm')

    def test_negative_sentiment(self):
        """
        Test the sentiment analyzer with overall negative sentences returns negative score
        """
        initialize_sentiment_analyzer()
        sentiment_analyzer = SentimentAnalyzer()
        sentiment_score = sentiment_analyzer(self.TEST_NEGATIVE_SENTENCES)
        self.assertLess(sentiment_score, 0)

    def test_positive_sentiment(self):
        """
        Test the sentiment analyzer with overall positive sentences returns positive score
        """
        initialize_sentiment_analyzer()
        sentiment_analyzer = SentimentAnalyzer()
        sentiment_score = sentiment_analyzer(self.TEST_POSITIVE_SENTENCES)
        self.assertGreater(sentiment_score, 0)

    def test_positive_negated_sentiment(self):
        """
        Test the sentiment analyzer with positive negated sentence returns negative score
        """
        initialize_sentiment_analyzer()
        sentiment_analyzer = SentimentAnalyzer()
        sentiment_score = sentiment_analyzer(self.TEST_POSITIVE_NEGATED_SENTENCE)
        self.assertLess(sentiment_score, 0)

    def test_negative_negated_sentiment(self):
        """
        Test the sentiment analyzer with negative negated sentence returns positive score
        """
        initialize_sentiment_analyzer()
        sentiment_analyzer = SentimentAnalyzer()
        sentiment_score = sentiment_analyzer(self.TEST_NEGATIVE_NEGATED_SENTENCE)
        self.assertGreater(sentiment_score, 0)



