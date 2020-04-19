"""
Fixed dict tests module
"""
from unittest import TestCase

from news_manager.lib.fixed_dict import FixedDict


class TestFixedDict(TestCase):
    """
    Fixed dict test cases implementation
    """
    def test_length(self):
        """
        Test len returns the length of the dictionary contained in the FixedDict
        """
        test_dict = FixedDict(dict(test1='test1', test2='test2'))
        self.assertEqual(len(test_dict), 2)

    def test_set_item_new_key(self):
        """
        Test trying to add an unexisting key raises error
        """
        test_dict = FixedDict(dict(test1='test1', test2='test2'))
        with self.assertRaises(KeyError):
            test_dict['test3'] = 'test3'

    def test_deleting_key_not_allowed(self):
        """
        Test trying to delete a key raises error
        """
        test_dict = FixedDict(dict(test1='test1', test2='test2'))
        with self.assertRaises(NotImplementedError):
            del test_dict['test2']

    def test_contains(self):
        """
        Test the contains method checks the key against the dictionary contained
        """
        test_dict = FixedDict(dict(test1='test1', test2='test2'))
        self.assertTrue('test2' in test_dict)
        self.assertFalse('test3' in test_dict)
