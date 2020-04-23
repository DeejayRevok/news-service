"""
NLP functions module
"""
from news_service_lib.models import NLPDoc
from stanza import Pipeline, Document

from nlp_service.nlp_celery_worker.celery_nlp_tasks import hydrate_new_with_entities, publish_hydrated_new, \
    process_content, hydrate_new_summary, hydrate_new_sentiment


class NlpService:
    """
    NLP service implementation
    """
    CELERY_NLP_PIPELINE = [process_content, hydrate_new_with_entities, hydrate_new_summary, hydrate_new_sentiment]

    def __init__(self):
        """
        Initialize the NLP service loading the language model
        """
        self._spanish_language = Pipeline('es')

    async def _process_text(self, text: str) -> Document:
        """
        Process a text with the language model

        Args:
            text: text to process

        Returns: processed text with NLP information

        """
        return self._spanish_language(text)

    async def get_processed_text(self, text: str) -> NLPDoc:
        """
        Get NLP data about the input text

        Args:
            text: text to extract NLP data

        Returns: NLP data extracted

        """
        doc = await self._process_text(text)
        return NLPDoc(sentences=[sentence.text for sentence in doc.sentences],
                      named_entities=[(entity.text, entity.type) for entity in doc.entities])

    async def hydrate_new(self, new: dict):
        """
        Hydrate the given new with NLP information

        Args:
            new: new to hydrate

        """
        hydrate_chain_start = self.CELERY_NLP_PIPELINE[0].s(new)
        previous_task = hydrate_chain_start
        for task in self.CELERY_NLP_PIPELINE[1:]:
            task_signature = task.s()
            previous_task.link(task_signature)
            previous_task = task_signature
        previous_task.link(publish_hydrated_new.s())
        hydrate_chain_start.delay()
