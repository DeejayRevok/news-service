"""
New model module
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator


@dataclass
class New:
    """
    New model
    """
    title: str
    content: str
    categories: list
    date: float

    def __iter__(self) -> Iterator[tuple]:
        """
        Get an iterator to the new properties

        Returns: iterator to current new properties

        """
        yield 'title', self.title
        yield 'content', self.content
        yield 'categories', self.categories
        yield 'date', self.date

    def dto(self, render_date_format: str) -> dict:
        """
        Get a dto for the current new

        Args:
            render_date_format: date formatter for the dto

        Returns: dto of the new

        """
        return dict(title=self.title,
                    content=self.content,
                    categories=self.categories,
                    date=datetime.fromtimestamp(self.date).strftime(render_date_format))
