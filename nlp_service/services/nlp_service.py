"""
NLP fuctions module
"""
from typing import Iterator

from news_service_lib.models import NamedEntity
from stanza import Pipeline, Document

from nlp_service.nlp_celery_worker.celery_nlp_tasks import hydrate_new_with_entities, publish_hydrated_new


class NlpService:
    """
    NLP service implementation
    """
    CELERY_NLP_PIPELINE = [hydrate_new_with_entities]

    def __init__(self):
        """
        Initialize the NLP service loading the language model
        """
        self.spanish_language = Pipeline('es')

    async def _process_text(self, text: str) -> Document:
        """
        Process a text with the language model

        Args:
            text: text to process

        Returns: processed text with NLP information

        """
        return self.spanish_language(text)

    async def get_named_entities(self, text: str) -> Iterator[NamedEntity]:
        """
        Get the named entities of the given text

        Args:
            text: text to extract the named entities from

        Returns: named entities extracted

        """
        doc = await self._process_text(text)
        return iter(set(map(lambda entity: NamedEntity(text=entity.text.lower(), type=entity.type), doc.entities)))

    async def hydrate_new(self, new: dict):
        """
        Hydrate the given new with NLP information

        Args:
            new: new to hydrate

        """
        hydrate_chain = self.CELERY_NLP_PIPELINE[0].s(new)
        for task in self.CELERY_NLP_PIPELINE[1:]:
            hydrate_chain.link(task.s())
        hydrate_chain.link(publish_hydrated_new.s())
        hydrate_chain.delay()
