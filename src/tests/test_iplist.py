"""Basic unit tests of IPList classes."""
# pylint: disable=invalid-name,import-error

import collections
import unittest

from foomuuri import IPList, IPLists


class TestIPLists(unittest.TestCase):
    """Test IPLists."""
    def setUp(self):
        """Prepare test fixture."""
        self.iplists = IPLists()

        self.sources_foo = ['https://foob.ar', 'https://foob.az']
        self.iplists['@foo'] = IPList(sources=self.sources_foo)

        self.sources_bar = ['https://arbo.of', 'https://azbp.of']
        self.iplists['@bar'] = IPList(sources=self.sources_bar)
        self.iplists['@bar'].options.start = False

    def test_index_getter(self):
        """Test index getter by iplist name."""
        self.assertEqual(self.iplists['@foo'].sources, self.sources_foo)
        self.assertEqual(self.iplists['@bar'].sources, self.sources_bar)

    def test_iter_names(self):
        """Test iterator over iplist names."""
        self.assertEqual(list(self.iplists), ['@foo', '@bar'])

    def test_items(self):
        """Test iterable over iplist entries (name, value tuples)."""
        self.assertIsInstance(self.iplists.items(), collections.abc.Iterable)
        self.assertListEqual(
            list(self.iplists.items()),
            [
                ('@foo', self.iplists['@foo']),
                ('@bar', self.iplists['@bar']),
            ],
        )

    def test_values(self):
        """Test iterable over iplist entries values."""
        self.assertIsInstance(self.iplists.values(), collections.abc.Iterable)
        self.assertListEqual(
            list(self.iplists.values()),
            [
                self.iplists['@foo'],
                self.iplists['@bar'],
            ],
        )

    def test_filter_names_by(self):
        """Test set of iplist names with specific iplist option value."""
        self.assertIsInstance(self.iplists.filter_names_by('start', True), set)
        self.assertEqual(self.iplists.filter_names_by('start', True), {'@foo'})
