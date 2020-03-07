from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(255))

    def __iter__(self):
        yield 'id', repr(self.id)
        yield 'username', repr(self.username)


def create_schema(db_engine):
    Base.metadata.tables['users'].create(db_engine, checkfirst=True)
