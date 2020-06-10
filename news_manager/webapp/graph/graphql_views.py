"""
GraphQL views module
"""
import asyncio

from aiohttp.web_app import Application
from aiohttp_graphql import GraphQLView
from graphene import Schema
from graphql.execution.executors.asyncio import AsyncioExecutor

from news_manager.webapp.graph.queries import Query

schema = Schema(query=Query)


def setup_routes(app: Application):
    """
    Add the graphql routes to the specified application

    Args:
        app: application to add routes

    """
    GraphQLView.attach(app,
                       schema=schema,
                       graphiql=True,
                       route_path='/graphql',
                       executor=AsyncioExecutor(loop=asyncio.get_event_loop()),
                       enable_async=True)
