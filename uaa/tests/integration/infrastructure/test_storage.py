"""
Storage test cases
"""
import unittest
from unittest import TestCase
from unittest.mock import patch

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from uaa.infrastructure.storage.sql_storage import SqlStorage

BASE = declarative_base()


class TestModel(BASE):
    """
    Test model
    """
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True)
    test1 = Column(String(50))
    test2 = Column(String(50))


class TestStorage(TestCase):

    TEST_1 = 'test_1'
    TEST_2 = 'test_2'

    @patch('uaa.infrastructure.storage.sql_storage.create_engine')
    def setUp(self, mock_create_engine):
        """
        Set up each test environment
        """
        mock_create_engine.return_value = create_engine('sqlite://')
        self.client = SqlStorage(host='', port=0, user='', password='', schema='')
        BASE.metadata.tables['test'].create(self.client.engine, checkfirst=True)

    def test_save(self):
        """
        Test if the save method persists the instance
        """
        self.client.save(TestModel(test1=self.TEST_1, test2=self.TEST_2))
        model_instances = list(self.client.get_all(TestModel))
        self.assertIsNotNone(model_instances)
        self.assertEqual(len(model_instances), 1)
        self.assertEqual(model_instances[0].test1, self.TEST_1)
        self.assertEqual(model_instances[0].test2, self.TEST_2)

    def test_get_all(self):
        """
        Check if the get all method returns all persisted instances
        """
        self.client.save(TestModel(test1='test_11', test2='test_12'))
        self.client.save(TestModel(test1='test_21', test2='test_22'))
        model_instances = list(self.client.get_all(TestModel))
        self.assertIsNotNone(model_instances)
        self.assertEqual(len(model_instances), 2)

    def test_get_one(self):
        """
        Check if the get one method returns the first stored instance
        """
        self.client.save(TestModel(test1=self.TEST_1, test2=self.TEST_2))
        self.client.save(TestModel(test1='test_21', test2='test_22'))
        model_instance = self.client.get_one(TestModel)
        self.assertIsNotNone(model_instance)
        self.assertEqual(model_instance.test1, self.TEST_1)
        self.assertEqual(model_instance.test2, self.TEST_2)

    def test_health_check(self):
        """
        Check if the health check returns true
        """
        self.assertTrue(self.client.health_check())


if __name__ == '__main__':
    unittest.main()
