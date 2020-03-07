from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from uaa.log_config import get_logger

LOGGER = get_logger()


class SqlStorage:
    DB_URL = 'mysql://{user}:{password}@{host}:{port}/{database}'

    def __init__(self, host, port, user, password, database):
        self.engine = create_engine(
            SqlStorage.DB_URL.format(user=user, password=password, host=host, port=port, database=database), echo=True)
        session = sessionmaker(bind=self.engine)
        self._session = session()

    def save(self, model_instance):
        self._session.add(model_instance)
        self._session.commit()
        self._session.flush()
        return model_instance

    def get(self, model, **filters):
        query = self._session.query(model)
        return query.filter_by(**filters).first()

    def health_check(self):
        try:
            self.engine.execute('SELECT 1 AS is_alive')
            return True
        except Exception as ex:
            LOGGER.error('Storage system is not available %s', str(ex))
            return False
