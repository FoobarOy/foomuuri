"""Basic unit tests of Converters."""
# pylint: disable=import-error

import unittest

from foomuuri import Converters


class TestConverters(unittest.TestCase):
    """Test converter helpers."""

    def test_canonical_iplist_name(self):
        """Test canonical_iplist_name."""
        self.assertEqual(Converters.canonical_iplist_name('@foo'), '@foo')
        self.assertEqual(Converters.canonical_iplist_name('foo'), '@foo')

    def test_str_yes_no_to_bool(self):
        """Test str_yes_no_to_bool."""
        self.assertTrue(Converters.str_yes_no_to_bool('yes'))
        self.assertFalse(Converters.str_yes_no_to_bool('no'))
        self.assertRaises(ValueError, Converters.str_yes_no_to_bool, '')
        self.assertRaises(ValueError, Converters.str_yes_no_to_bool, 'invalid')
