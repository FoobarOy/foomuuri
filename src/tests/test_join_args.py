"""Basic unit tests of join_args()."""
# pylint: disable=import-error

import pathlib
import unittest

from foomuuri import join_args


class TestJoinArgs(unittest.TestCase):
    """Test join_args()."""
    def test_valid(self):
        """Test valid outcomes."""
        self.assertEqual(join_args([]), '')
        self.assertEqual(join_args(['ab', 'cd']), 'ab cd')
        self.assertEqual(join_args(['ab', pathlib.PosixPath('cd')]), 'ab cd')

    def test_invalid(self):
        """Test invalid outcomes."""
        self.assertRaises(TypeError, join_args, 'ab')
