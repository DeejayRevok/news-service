"""
GraphQL queries entry point
"""
from news_manager.webapp.graph.queries.news import NewsQuery


class Query(NewsQuery):
    """
    The main GraphQL query point.
    """
