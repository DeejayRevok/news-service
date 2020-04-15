"""
News views request schemas module
"""
from marshmallow import Schema, fields


class PutUpdateNewSchema(Schema):
    """
    Class that describes the schema of the put update new request
    """
    title = fields.Str(description="Title of the new to update")
    entities = fields.List(fields.Dict, description="List of named entities to update in the new")
