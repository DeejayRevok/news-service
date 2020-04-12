"""
NLP request schemas module
"""
from marshmallow import Schema, fields


class PostGetEntitiesSchema(Schema):
    """
    Class that describes the schema of the get entities request
    """
    text = fields.Str(description="Text to extract named entities")


class PutHydrateNewSchema(Schema):
    """
    Class that describes the schema of the put hydrate new request
    """
    title = fields.Str(description='New title')
    content = fields.Str(description='New text content')
    categories = fields.List(fields.Str, description='New categories')
    date = fields.Float(description='New date timestamp')
    entities = fields.List(fields.Dict, description='New named entities', allow_none=True)
