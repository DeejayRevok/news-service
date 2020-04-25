"""
NLP request schemas module
"""
from marshmallow import Schema, fields


class PostProcessTextSchema(Schema):
    """
    Class that describes the schema of the process text request
    """
    text = fields.Str(description="Text to process")


class PutHydrateNewSchema(Schema):
    """
    Class that describes the schema of the put hydrate new request
    """
    title = fields.Str(description='New title')
    content = fields.Str(description='New text content')
    source = fields.Str(description='New source')
    date = fields.Float(description='New date timestamp')
    summary = fields.Str(description='New summary', allow_none=True)
    sentiment = fields.Float(description='New content sentiment score', allow_none=True)
    entities = fields.List(fields.Dict, description='New named entities', allow_none=True)
