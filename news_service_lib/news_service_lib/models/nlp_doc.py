from dataclasses import dataclass
from typing import List


@dataclass
class NLPDoc:

    sentences: list
    named_entities: List[tuple]

    def __iter__(self):
        yield 'sentences', self.sentences
        yield 'named_entities', self.named_entities
