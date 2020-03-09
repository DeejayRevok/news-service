"""
SQL database client module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker

from uaa.log_config import get_logger

LOGGER = get_logger()


class SqlStorage:
    """
    SQL storage client implementation
    """
    DB_URL = 'mysql://{user}:{password}@{host}:{port}/{database}'

    def __init__(self, host: str, port: int, user: str, password: str, schema: str):
        """
        Database client initializer

        Args:
            host: database service host address
            port: database service port
            user: database access user
            password: database access password
            schema: database schema name
        """
        self.engine = create_engine(
            SqlStorage.DB_URL.format(user=user, password=password, host=host, port=port, database=schema), echo=True)
        session = sessionmaker(bind=self.engine)
        self._session = session()

    def save(self, model_instance):
        """
        Save the specified model to the database

        Args:
            model_instance: instance to save

        Returns: persisted instance

        """
        self._session.add(model_instance)
        self._session.commit()
        self._session.flush()
        return model_instance

    def get_one(self, model, **filters):
        """
        Get one persistence instance matching the given filters

        Args:
            model: model base class
            **filters: filters to apply

        Returns: instance filtered

        """
        query = self._session.query(model)
        return query.filter_by(**filters).first()

    def health_check(self) -> bool:
        """
        Check if the storage is available

        Returns: True if the storage is available, False otherwise

        """
        try:
            self.engine.execute('SELECT 1 AS is_alive')
            return True
        except Exception as ex:
            LOGGER.error('Storage system is not available %s', str(ex))
            return False
