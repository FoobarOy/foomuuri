"""Test iplist_output_values()."""

# pylint: disable=invalid-name,import-error

import copy
import time
import unittest.mock

import foomuuri
from foomuuri import INTERNAL as BASE_INTERNAL

from src.tests.test_iplist_cache_refresh import source_cache


@unittest.mock.patch(
    'foomuuri.INTERNAL', new_callable=lambda: copy.deepcopy(BASE_INTERNAL)
)
class TestIPListOutputValues(unittest.TestCase):
    """Test iplist_output_values()."""

    def setUp(self):
        """Prepare test fixtures."""
        self.now = int(time.time())
        self.url = 'https://foo.bar/iplist'
        self.url_missing_ok = f'{self.url}|missing-ok'

    @staticmethod
    def run_output(
        sources,
        cache,
        iplist_name,
        force=0,
    ):
        """Call iplist_output_values() with mocked IO."""
        foomuuri.INTERNAL.command = 'iplist'
        foomuuri.INTERNAL.force = force
        iplists = foomuuri.IPLists()
        iplists[iplist_name] = foomuuri.IPList(sources=sources)
        update_only = set()
        currently_active = {iplist_name}
        with (
            unittest.mock.patch('foomuuri.warning') as warning,
            unittest.mock.patch('foomuuri.fail') as fail,
            unittest.mock.patch('foomuuri.verbose') as verbose,
            unittest.mock.patch('foomuuri.OUT', new=[]),
            unittest.mock.patch(
                'foomuuri.iplist_apply_values', return_value=0
            ),
        ):
            ret = foomuuri.iplist_output_values(
                iplists, cache, currently_active, update_only
            )
        return ret, warning, fail, verbose

    def test_set_single_missing_ok_empty(self, *_):
        """Test warning and rc 0 for |missing-ok source with empty content."""
        cache = source_cache(self.url_missing_ok)
        ret, warning, fail, verbose = self.run_output(
            sources=[self.url_missing_ok],
            cache=cache,
            iplist_name='@foo',
        )
        self.assertEqual(ret, 0)
        warning.assert_called_once_with('Iplist "@foo" is empty')
        fail.assert_not_called()
        verbose.assert_not_called()

    def test_set_single_no_missing_ok_empty(self, *_):
        """Test fail and rc 2 for source with empty content."""
        cache = source_cache(self.url)
        ret, warning, fail, verbose = self.run_output(
            sources=[self.url],
            cache=cache,
            iplist_name='@foo',
        )
        self.assertEqual(ret, 2)
        fail.assert_called_once_with('Iplist "@foo" is empty', False)
        warning.assert_not_called()
        verbose.assert_not_called()

    def test_set_mixed_sources_empty(self, *_):
        """Test fail and rc 2 for mixed sources with empty content."""
        optional = self.url_missing_ok
        required = 'https://required.example/list'
        cache = source_cache(optional, required)
        ret, warning, fail, verbose = self.run_output(
            sources=[optional, required],
            cache=cache,
            iplist_name='@foo',
        )
        self.assertEqual(ret, 2)
        fail.assert_called_once_with('Iplist "@foo" is empty', False)
        warning.assert_not_called()
        verbose.assert_not_called()

    def test_set_clean_soft(self, *_):
        """Test verbose skip update message with --soft (force<0)."""
        cache = source_cache(self.url)
        ret, warning, fail, verbose = self.run_output(
            sources=[self.url],
            cache=cache,
            iplist_name='@foo',
            force=-1,
        )
        self.assertEqual(ret, 0)
        warning.assert_not_called()
        fail.assert_not_called()
        verbose.assert_called_once_with(
            'Iplist "@foo" is clean, skipping update'
        )

    def test_set_dirty_soft_updates(self, *_):
        """Test dirty cache updates with --soft (force<0)."""
        cache = source_cache(self.url, ip={'10.0.0.1': self.now})
        cache[self.url]['dirty'] = True
        ret, warning, fail, verbose = self.run_output(
            sources=[self.url],
            cache=cache,
            iplist_name='@foo',
            force=-1,
        )
        self.assertEqual(ret, 0)
        warning.assert_not_called()
        fail.assert_not_called()
        verbose.assert_called_once_with('Updating iplist "@foo", 1 entries')

    def test_set_nonempty_updates(self, *_):
        """Test verbose update message for non-empty set."""
        cache = source_cache(self.url, ip={'10.0.0.1': self.now})
        ret, warning, fail, verbose = self.run_output(
            sources=[self.url],
            cache=cache,
            iplist_name='@foo',
        )
        self.assertEqual(ret, 0)
        warning.assert_not_called()
        fail.assert_not_called()
        verbose.assert_called_once_with('Updating iplist "@foo", 1 entries')
