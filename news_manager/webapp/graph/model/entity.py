"""
Named entity graphql model module
"""
from graphene import ObjectType, String


class Entity(ObjectType):
    """
    Named entity graphql model implementation
    """
    text = String(description="Named entity text")
    type = String(description="Named entity type")
