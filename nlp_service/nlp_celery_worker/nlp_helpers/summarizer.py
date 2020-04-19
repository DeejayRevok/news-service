import math
import string
from typing import List

import numpy as np
import networkx as nx
from nltk import download
from nltk.cluster import cosine_distance
from nltk.corpus import stopwords


def initialize_summarizer():
    """
    Initialize the summarizer NLP resources
    """
    download('stopwords')


def generate_summary_from_sentences(sentences: List[str], summary_sentences: int = 5) -> str:
    """
    Generate the summary of the input sentences with the given number of sentences in the output
    Algorithm explanation:
    https://towardsdatascience.com/understand-text-summarization-and-create-your-own-summarizer-in-python-b26a9f09fc70

    Args:
        sentences: sentences to get summary
        summary_sentences: number of the sentences of the output summary

    Returns: sentences summary

    """
    stop_words = stopwords.words('spanish')
    sentence_similarity_matrix = _build_similarity_matrix(sentences, stop_words)

    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_matrix)
    scores = nx.pagerank(sentence_similarity_graph)

    ranked_sentence = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)

    summarize_text_sentences = []
    for i in range(summary_sentences):
        summarize_text_sentences.append(ranked_sentence[i][1])

    return ' '.join(summarize_text_sentences)


def _build_similarity_matrix(sentences: List[str], stop_words: List[str]) -> np.ndarray:
    """
    Build the similarity matrix of the sentences with the given stop words

    Args:
        sentences: sentences to build similarity matrix
        stop_words: stop words to ignore

    Returns: similarity matrix of the given sentences

    """
    similarity_matrix = np.zeros((len(sentences), len(sentences)))

    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2:
                continue
            similarity_matrix[idx1][idx2] = _sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix


def _sentence_similarity(sent1: str, sent2: str, stop_words: list = None) -> int:
    """
    Get the sentence similarity score using the cosine distance of the sentences vector

    Args:
        sent1: first sentence to compare
        sent2: second sentence to compare
        stop_words: words to ignore

    Returns: sentence similarity

    """
    if stop_words is None:
        stop_words = list()

    sent1 = [w.translate(str.maketrans('', '', string.punctuation)).lower() for w in sent1.split(' ')]
    sent2 = [w.translate(str.maketrans('', '', string.punctuation)).lower() for w in sent2.split(' ')]

    all_words = list(set(sent1 + sent2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    for w in sent1:
        if w in stop_words:
            continue
        vector1[all_words.index(w)] += 1

    for w in sent2:
        if w in stop_words:
            continue
        vector2[all_words.index(w)] += 1

    result = cosine_distance(vector1, vector2)
    return result if not math.isnan(result) else 0.0
