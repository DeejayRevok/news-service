"""
NLP document module
"""
from dataclasses import dataclass
from typing import List


@dataclass
class NLPDoc:
    """
    NLPDoc model class
    """
    sentences: list
    named_entities: List[tuple]

    def __iter__(self) -> iter:
        """
        Get an iterator to the nlp document properties

        Returns: iterator to document properties

        """
        yield 'sentences', self.sentences
        yield 'named_entities', self.named_entities
