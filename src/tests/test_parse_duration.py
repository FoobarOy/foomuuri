"""Basic unit tests of parse_duration()."""
# pylint: disable=import-error

import unittest

from foomuuri import parse_duration


class TestParseDuration(unittest.TestCase):
    """Test parse_duration()."""
    def test_valid_duration(self):
        """Test valid outcomes."""
        self.assertEqual(parse_duration(' 0s ', fallback=None), 0)
        self.assertEqual(parse_duration(' 1s ', fallback=0), 1)
        self.assertEqual(parse_duration(' 1h 1m ', fallback=0), 3660)
        self.assertEqual(parse_duration(' 1w1d1h1m1s ', fallback=0), 694861)

    def test_invalid_duration(self):
        """Test invalid outcomes."""
        self.assertIsNone(parse_duration('', fallback=None))
        self.assertIsNone(parse_duration('1day', fallback=None))
        self.assertIsNone(parse_duration('1y', fallback=None))
        self.assertIsNone(parse_duration('s', fallback=None))
        self.assertIsNone(parse_duration('1s1h', fallback=None))
