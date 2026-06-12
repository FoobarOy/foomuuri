"""Basic unit tests of Validators."""
# pylint: disable=import-error

import unittest

from foomuuri import Validators


class TestValidators(unittest.TestCase):
    """Test assert helpers."""

    def assert_valid_invalid(self, test, valid_cases, invalid_cases):
        """Helper function to reduce repetition."""
        for case in valid_cases:
            with self.subTest(case):
                self.assertTrue(test(case), f'Expected {case!r} to be valid')
        for case in invalid_cases:
            with self.subTest(case):
                self.assertFalse(
                    test(case), f'Expected {case!r} to be invalid'
                )

    def test_str_zone_name(self):
        """Test for str is zone name."""
        invalid = ['', 'word word', '3word', 'w#ord', '_./_']
        valid = ['wo_123_rd', 'w./_']
        self.assert_valid_invalid(Validators.str_zone_name, valid, invalid)

    def test_str_iplist_name(self):
        """Test for str is iplist name."""
        invalid = ['', '@', '@w w', '@kääk', '@3word']
        valid = ['@word', '@_', '@_./-']
        self.assert_valid_invalid(Validators.str_iplist_name, valid, invalid)

    def test_str_interface_name(self):
        """Test for str is linux interface name."""
        invalid = [
            '',
            'word word',
            'word\nword',
            'word/word',
            'word"word',
            'word\\word',
            'wordwordwordword',
        ]
        valid = ['eth0', ':', '@', 'kääk']
        self.assert_valid_invalid(
            Validators.str_interface_name, valid, invalid
        )

    def test_str_words(self):
        """Test for str is one or more words."""
        invalid = ['']
        valid = ['word', 'word word']

        self.assert_valid_invalid(Validators.str_words, valid, invalid)

    def test_has_elements(self):
        """Test for list or set is not empty."""
        invalid = [[], {}]
        valid = [['a'], ['a', 'b'], {'a'}, {'a', 'b'}]

        self.assert_valid_invalid(Validators.has_elements, valid, invalid)

    def test_int_positive_or_zero(self):
        """Test for int is not negative."""
        invalid = [-1]
        valid = [0, 1]
        self.assert_valid_invalid(
            Validators.int_positive_or_zero, valid, invalid
        )

    def test_int_positive(self):
        """Test for int is positive."""
        invalid = [-1, 0]
        valid = [1]
        self.assert_valid_invalid(Validators.int_positive, valid, invalid)

    def test_str_yes_no(self):
        """Test for str is 'yes' or 'no'."""
        invalid = ['', 'maybe', 'YES']
        valid = ['yes', 'no']
        self.assert_valid_invalid(Validators.str_yes_no, valid, invalid)
