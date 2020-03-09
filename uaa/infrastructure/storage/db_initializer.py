"""
Module which initializes the database schema
"""
import inspect

from sqlalchemy.engine import Engine

from uaa import models


def initialize_db(db_engine: Engine):
    """
    Initialize the database schema

    Args:
        db_engine: database engine instance

    """
    for _, module in inspect.getmembers(models, inspect.ismodule):
        module.create_schema(db_engine)
