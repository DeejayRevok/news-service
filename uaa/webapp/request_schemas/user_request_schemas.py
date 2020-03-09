"""
User request schemas module
"""
from marshmallow import Schema, fields


class PostCreateUserSchema(Schema):
    """
    Class that describes the schema of the post create user request
    """
    username = fields.Str(description="User name")
    password = fields.Str(description="User password")
