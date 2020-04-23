"""
Sentiment analysis module
"""
from typing import List, Iterator, Tuple

from googletrans import Translator
from nltk import download
from nltk.sentiment import SentimentIntensityAnalyzer

from nlp_service.log_config import get_logger

LOGGER = get_logger()


def initialize_sentiment_analyzer():
    """
    Initialize the sentiment analyzer downloading the required resources (VADER lexicon)
    """
    LOGGER.info('Downloading VADER lexicon')
    download('vader_lexicon')


def compute_overall_sentiment_sentences(sentences: List[str]) -> float:
    """
    Compute the overall sentiment score for the input sentences

    Args:
        sentences: sentences to compute overall sentiment

    Returns: sum of the sentences sentiments

    """
    LOGGER.info('Starting sentiment analysis for %d sentences', len(sentences))
    return sum(_analyze_sentiments_sentences(_translate_sentences(sentences)))


def _translate_sentences(sentences: List[str]) -> Iterator[str]:
    """
    Translate the input sentences in spanish to english

    Args:
        sentences: spanish sentences

    Returns: english translated sentences

    """
    translator = Translator()
    return map(lambda sent: sent.text, translator.translate(sentences, src='es', dest='en'))


def _analyze_sentiments_sentences(sentences: Iterator[str]) -> List[Tuple[str, float]]:
    """
    Analyze the sentiment score of the input sentences

    Args:
        sentences: sentences to analyze sentiment

    Returns: iterator to the sentiment score of each sentence

    """
    sentiment_analyzer = SentimentIntensityAnalyzer()
    for sentence in sentences:
        yield sentiment_analyzer.polarity_scores(sentence)['compound']
