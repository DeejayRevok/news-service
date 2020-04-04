from dataclasses import dataclass


@dataclass
class New:

    title: str
    content: str
    categories: list
    date: float

    def __iter__(self):
        yield 'title', self.title
        yield 'content', self.content
        yield 'categories', self.categories
        yield 'date', self.date
