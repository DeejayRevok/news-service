"""
Authentication request schemas module
"""
from marshmallow import Schema, fields


class PostAuthSchema(Schema):
    """
    Class that describes the schema of the post authenticate request
    """
    username = fields.Str(description="User name")
    password = fields.Str(description="User password")


class PostValidateTokenSchema(Schema):
    """
    Class that describes the schema of the post validate token request
    """
    token = fields.Str(description="JWT token to validate")
