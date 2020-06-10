"""
Graphql news queries module
"""
from typing import List

from graphene import ObjectType, List as GraphList, Field, Argument, String
from graphql import ResolveInfo

from news_manager.webapp.graph.model.new import New
from news_manager.webapp.graph.utils.custom_date_time import DATE_FORMAT


class NewsQuery(ObjectType):
    """
    GraphQL news queries implementation
    """
    news = GraphList(New, description='Available news')
    new = Field(New,
                title=Argument(String),
                description='New with the given title')

    async def resolve_news(self, info: ResolveInfo) -> List[dict]:
        """
        News list graphql query

        Args:
            info: query information

        Returns: list of queried news

        """
        app = info.context['request'].app
        return [new.dto(DATE_FORMAT) for new in await app['news_service'].get_news()]

    async def resolve_new(self, info: ResolveInfo, title: int) -> dict:
        """
        Single new graphql query

        Args:
            info: query information
            title: title to get new

        Returns: queried new

        """
        app = info.context['request'].app
        return dict(await app['news_service'].get_new_by_title(title))

