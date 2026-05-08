"""Basic unit tests of parse_duration() and seconds_to_duration()."""
# pylint: disable=import-error

import unittest

from foomuuri import parse_duration, seconds_to_duration


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


class TestSecondsToDuration(unittest.TestCase):
    """Test seconds_to_duration()."""

    def test_valid_seconds(self):
        """Test valid outcomes."""
        self.assertEqual(seconds_to_duration(0), '0s')
        self.assertEqual(seconds_to_duration(1), '1s')
        self.assertEqual(seconds_to_duration(42), '42s')
        self.assertEqual(seconds_to_duration(61), '1m01s')
        self.assertEqual(seconds_to_duration(3600), '1h00m00s')
        self.assertEqual(seconds_to_duration(99999), '1d03h46m39s')
        self.assertEqual(seconds_to_duration(999999), '11d13h46m39s')
        self.assertEqual(seconds_to_duration(9999999), '115d17h46m39s')
