"""
Summary generation operations module
"""
import math
import string
from statistics import mean
from typing import List, Iterator, Tuple

import numpy as np
import networkx as nx
from nltk import download
from nltk.cluster import cosine_distance
from nltk.corpus import stopwords

from nlp_service.log_config import get_logger

LOGGER = get_logger()


def initialize_summarizer():
    """
    Initialize the summarizer NLP resources
    """
    LOGGER.info('Downloading stopwords...')
    download('stopwords')


def generate_summary_from_sentences(sentences: List[str]) -> str:
    """
    Generate the summary of the input sentences with the given number of sentences in the output
    Base algorithm explanation:
    https://towardsdatascience.com/understand-text-summarization-and-create-your-own-summarizer-in-python-b26a9f09fc70

    Args:
        sentences: sentences to get summary

    Returns: sentences summary

    """
    LOGGER.info('Generating summary for %d input sentences', len(sentences))
    stop_words = stopwords.words('spanish')

    if stop_words is None:
        stop_words = list()

    preprocessed_sentences = list(_preprocess_sentences(sentences, stop_words))

    sentence_similarity_matrix = _build_similarity_matrix(
        map(lambda prep_sent: prep_sent[0], preprocessed_sentences),
        stop_words)

    sentence_distance_graph = nx.from_numpy_array(sentence_similarity_matrix)
    scores = nx.pagerank(sentence_distance_graph)

    for i, preprocessed_sentence in enumerate(preprocessed_sentences):
        scores[i] = scores[i] * preprocessed_sentence[1]

    summary_sentences_num = round(len(sentences) / 4)
    summary_sentences_num = summary_sentences_num if summary_sentences_num >= 2 else 2
    summary_sentences_num = summary_sentences_num if summary_sentences_num <= 10 else 10

    ranked_scores = {k: v for k, v in sorted(scores.items(), key=lambda item: item[1], reverse=True)}
    ranked_sentences = list(ranked_scores.keys())
    qualifiers = ranked_sentences[:summary_sentences_num]
    non_qualifiers = ranked_sentences[summary_sentences_num:]

    _clean_qualifiers(qualifiers, non_qualifiers, sentence_similarity_matrix, preprocessed_sentences)

    summarize_text_sentences = []
    for i in sorted(qualifiers):
        summarize_text_sentences.append(sentences[i])

    return ' '.join(summarize_text_sentences)


def _preprocess_sentences(sentences: List[str], stop_words: List[str]) -> Iterator[Tuple[List[str], float]]:
    """
    Preprocess sentences transforming them into a list of cleaned words and calculating their entropy

    Args:
        sentences: sentences to preprocess
        stop_words: stopwords to calculate the entropy of each sentence

    Returns: iterator to tuples containing the sentence preprocessed words and its entropy

    """
    for sentence in sentences:
        sentence_words = [word.translate(str.maketrans('', '', string.punctuation)).lower() for word in
                          sentence.split(' ')]
        yield sentence_words, _get_sentence_entropy(sentence_words, stop_words)


def _get_sentence_entropy(sentence: List[str], stop_words: List[str]) -> float:
    """
    Get the sentence entropy in terms of useful words per sentence

    Args:
        sentence: sentence to get entropy
        stop_words: useless words

    Returns: sentence entropy

    """
    return mean(map(lambda word: 1 if word not in stop_words else 0, sentence))


def _build_similarity_matrix(sentences: Iterator[List[str]], stop_words: List[str]) -> np.ndarray:
    """
    Build the similarity matrix of the sentences with the given stop words

    Args:
        sentences: sentences to build similarity matrix
        stop_words: stop words to ignore

    Returns: similarity matrix of the given sentences

    """
    sentences = list(sentences)
    similarity_matrix = np.zeros((len(sentences), len(sentences)))

    for idx1, _ in enumerate(sentences):
        for idx2, _ in enumerate(sentences):
            if idx1 == idx2:
                continue
            similarity_matrix[idx1][idx2] = _sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix


def _sentence_similarity(sent1: List[str], sent2: List[str], stop_words: list) -> int:
    """
    Get the sentence similarity score using the cosine distance of the sentences vector

    Args:
        sent1: first sentence to compare
        sent2: second sentence to compare
        stop_words: words to ignore

    Returns: sentence similarity

    """

    all_words = list(set(sent1 + sent2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    for word in sent1:
        if word in stop_words:
            continue
        vector1[all_words.index(word)] += 1

    for word in sent2:
        if word in stop_words:
            continue
        vector2[all_words.index(word)] += 1

    result = cosine_distance(vector1, vector2)
    return 1 - result if not math.isnan(result) else 0.0


def _clean_qualifiers(qualifiers: List[int], non_qualifiers: List[int], sentence_similarity_matrix: np.ndarray,
                      preprocessed_sentences: List[Tuple[List[str], float]]):
    """
    Clean the summary sentence qualifiers in order to remove similar sentences (more of 75% of the sentence is equal)

    Args:
        qualifiers: summary sentence qualifiers
        non_qualifiers: non summary sentence qualifiers
        sentence_similarity_matrix: all sentences similarity matrix
        preprocessed_sentences: all preprocessed sentences

    """
    qualifiers_similarity_matrix = sentence_similarity_matrix.take([qualifiers, list(reversed(qualifiers))])
    similar_qualifiers = set(map(lambda indexes: tuple(sorted(indexes)),
                                 filter(lambda indexes: len(indexes) > 0,
                                        np.where(qualifiers_similarity_matrix > 0.75))))
    if len(non_qualifiers) > 0 and len(similar_qualifiers) > 0:
        for idx1, idx2 in set(map(lambda indexes: tuple(sorted(indexes)), list(similar_qualifiers))):
            if len(non_qualifiers) > 0:
                if preprocessed_sentences[qualifiers[idx1]][1] >= preprocessed_sentences[qualifiers[idx2]][1]:
                    del qualifiers[idx2]
                else:
                    del qualifiers[idx1]
                qualifiers.append(non_qualifiers.pop(0))
        _clean_qualifiers(qualifiers, non_qualifiers, sentence_similarity_matrix, preprocessed_sentences)
