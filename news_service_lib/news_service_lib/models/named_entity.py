from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class NamedEntity:

    text: str
    type: str

    def __iter__(self):
        yield 'text', self.text
        yield 'type', self.type
