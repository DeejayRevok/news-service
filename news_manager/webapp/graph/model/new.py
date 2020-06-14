"""
New graphql model module
"""
from typing import List
from graphene import ObjectType, String, Boolean, List as GraphList, Float
from graphql import ResolveInfo

from news_manager.webapp.graph.model.entity import Entity
from news_manager.webapp.graph.utils.custom_date_time import CustomDateTime


class New(ObjectType):
    """
    New graphql model implementation
    """
    title = String(description="New title. unique for all the news")
    content = String(description="New full content")
    source = String(description="New source name")
    date = CustomDateTime(description="New publish date and time")
    hydrated = Boolean(description="True if the new has been hydrated with the NLP data, false otherwise")
    entities = GraphList(Entity, description='New named entities')
    summary = String(description='New content summary')
    sentiment = Float(description="New sentiment intensity")

    async def resolve_entities(self, info: ResolveInfo) -> List[dict]:
        """
        Fetch the new named entities

        Args:
            info: graphql query info

        Returns: new named entities

        """
        app = info.context['request'].app
        new = await app['news_service'].get_new_by_title(self['title'])
        return [dict(entity) for entity in new.entities]
