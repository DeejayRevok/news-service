"""
User model module
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """
    User model
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(255))

    def __iter__(self) -> iter:
        """
        Iterate over the model properties

        Returns: iterator to the model properties

        """
        yield 'id', repr(self.id)
        yield 'username', repr(self.username)


def create_schema(db_engine: Engine):
    """
    Create the user model table

    Args:
        db_engine: database engine

    """
    Base.metadata.tables['users'].create(db_engine, checkfirst=True)
