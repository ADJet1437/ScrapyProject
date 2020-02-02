__author__ = 'graeme'

import unittest
from alascrapy.alascrapy_lib.utils import Utils
from scrapy.selector import SelectorList, Selector
from mock import Mock


class UtilTest(unittest.TestCase):

    def test_first_match_unicode_list(self):
        sample_list = SelectorList()
        sample_list.extract = Mock(return_value=[u'one', u'two', u'three', u'four'])

        first_match = Utils.first_match(sample_list)
        assert first_match == u'one', "First item from unicode list incorrect!"

    def test_first_match_string_list(self):
        sample_list = SelectorList()
        sample_list.extract = Mock(return_value=['one', 'two', 'three', 'four'])

        first_match = Utils.first_match(sample_list)
        assert first_match == 'one', "First item from string list incorrect!"

    def test_first_match_mixed_list(self):
        sample_list = SelectorList()
        sample_list.extract = Mock(return_value=[u'one', 'two', u'three', 'four'])

        first_match = Utils.first_match(sample_list)
        assert first_match == u'one', "First item from mixed list incorrect!"

    def test_first_match_empty_list(self):
        sample_list = SelectorList([])

        first_match = Utils.first_match(sample_list)
        assert first_match is None, "First item from empty list incorrect!"

    def test_trim_list_unicode_list(self):
        sample_list = SelectorList()
        sample_list.extract = Mock(return_value=[u'  one  ', u'  two point five ', u'three    ', u'   four'])

        desired_list = [u'one', u'two point five', u'three', u'four']
        trimmed_list = Utils.trim_list(sample_list)
        assert desired_list == trimmed_list, "Unicode list incorrect trimmed: {%s} vs {%s}" % (
            ', '.join(map(unicode, desired_list)), ', '.join(map(unicode, trimmed_list)))

    def test_trim_list_string_list(self):
        sample_list = SelectorList()
        sample_list.extract = Mock(return_value=['  one  ', '  two point five ', 'three    ', '   four'])

        desired_list = ['one', 'two point five', 'three', 'four']
        trimmed_list = Utils.trim_list(sample_list)
        assert desired_list == trimmed_list, "String list incorrect trimmed: {%s} vs {%s}" % (
            ', '.join(map(str, desired_list)), ', '.join(map(str, trimmed_list)))

    def test_trim_list_mixed_list(self):
        sample_list = SelectorList()
        sample_list.extract = Mock(return_value=['  one  ', u'  two point five ', 'three    ', u'   four'])

        desired_list = ['one', 'two point five', 'three', 'four']
        trimmed_list = Utils.trim_list(sample_list)
        assert desired_list == trimmed_list, "Mixed list incorrect trimmed"

    def test_trim_list_empty_list(self):
        sample_list = SelectorList()
        sample_list.extract = Mock(return_value=[])

        trimmed_list = Utils.trim_list(sample_list)
        assert trimmed_list is None, "Empty list incorrect trimmed"

    @classmethod
    def suite(cls):

        tests = ['test_first_match_unicode_list',
                 'test_first_match_string_list',
                 'test_first_match_mixed_list',
                 'test_first_match_empty_list',
                 'test_trim_list_unicode_list',
                 'test_trim_list_string_list',
                 'test_trim_list_mixed_list',
                 'test_trim_list_empty_list']

        return unittest.TestSuite(map(UtilTest, tests))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(UtilTest.suite())
