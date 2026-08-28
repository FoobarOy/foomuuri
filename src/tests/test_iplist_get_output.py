"""Test iplist get_url_or_file() and iplist_output_values().

Cover iplist cache management and user interaction behaviour.
"""

# pylint: disable=invalid-name,import-error

import copy
import time
import unittest.mock

import foomuuri
from foomuuri import INTERNAL as BASE_INTERNAL


@unittest.mock.patch(
    'foomuuri.INTERNAL', new_callable=lambda: copy.deepcopy(BASE_INTERNAL)
)
class TestIplistGetOutput(unittest.TestCase):
    """Test get_url_or_file() and iplist_output_values() behaviour."""

    def setUp(self):
        """Prepare test fixtures."""
        self.now = int(time.time())
        self.url = 'https://foo.bar/iplist'
        self.url_missing_ok = f'{self.url}|missing-ok'

    @staticmethod
    def run_get(url, cache, content, force=0):
        """Call get_url_or_file() with mocked get_url()."""
        foomuuri.INTERNAL.force = force
        options = foomuuri.IPListSourceOptions()
        options.timeout = 1000
        options.refresh = 1000
        with (
            unittest.mock.patch('foomuuri.get_url', return_value=content),
            unittest.mock.patch('foomuuri.warning') as warning,
            unittest.mock.patch('foomuuri.verbose') as verbose,
        ):
            foomuuri.get_url_or_file(url, options, cache)
        return cache.get(url), warning, verbose

    @staticmethod
    def run_output(
        sources,
        cache,
        setname,
        force=0,
    ):
        """Call iplist_output_values() with mocked IO."""
        foomuuri.INTERNAL.command = 'iplist'
        foomuuri.INTERNAL.force = force
        iplists = foomuuri.IPLists()
        iplists[setname] = foomuuri.IPList(sources=sources)
        update_only = set()
        currently_active = {setname}
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

    @staticmethod
    def source_cache(*sources, ip=None, refresh=None):
        """Return cache dict with one entry per source."""
        entry = {'ip': {} if ip is None else ip, 'dirty': False}
        if refresh is not None:
            entry['refresh'] = refresh
        return {source: copy.deepcopy(entry) for source in sources}

    def test_empty_url_missing_ok(self, *_):
        """Test no warning for empty source with |missing-ok.

        Pre-existing cache is overwritten.
        """
        cache = self.source_cache(
            self.url_missing_ok, ip={'10.0.0.1': self.now}, refresh=self.now
        )
        entry, warning, verbose = self.run_get(
            url=self.url_missing_ok, cache=cache, content=''
        )
        self.assertFalse(entry['ip'])
        self.assertTrue(entry['dirty'])
        warning.assert_not_called()
        verbose.assert_called_once_with(
            f'Iplist content for "{self.url_missing_ok}" refreshed, 0 entries'
        )

    def test_empty_url_no_missing_ok(self, *_):
        """Test warning for empty source without |missing-ok.

        Pre-existing cache is overwritten.
        """
        cache = self.source_cache(self.url, ip={'10.0.0.1': self.now})
        entry, warning, verbose = self.run_get(
            url=self.url, cache=cache, content=''
        )
        self.assertFalse(entry['ip'])
        self.assertTrue(entry['dirty'])
        warning.assert_called_once_with(
            f'No IP addresses listed in "{self.url}"'
        )
        verbose.assert_called_once_with(
            f'Iplist content for "{self.url}" refreshed, 0 entries'
        )

    def test_nonempty_url_no_missing_ok(self, *_):
        """Test cache stores new values from source without |missing-ok."""
        cache = self.source_cache(self.url, ip={'10.0.0.1': self.now})
        entry, warning, verbose = self.run_get(
            url=self.url, cache=cache, content='10.0.0.9\n'
        )
        self.assertIn('10.0.0.9', entry['ip'])
        self.assertTrue(entry['dirty'])
        warning.assert_not_called()
        verbose.assert_called_once_with(
            f'Iplist content for "{self.url}" refreshed, 1 entries'
        )

    def test_url_cached_soft(self, *_):
        """Test using cache values with --soft (force<0)."""
        cache = self.source_cache(
            self.url, ip={'10.0.0.1': self.now}, refresh=self.now
        )
        entry, warning, verbose = self.run_get(
            url=self.url, cache=cache, content='10.0.0.9\n', force=-1
        )
        self.assertIn('10.0.0.1', entry['ip'])
        self.assertFalse(entry['dirty'])
        warning.assert_not_called()
        verbose.assert_called_once_with(f'Using cached value for "{self.url}"')

    def test_url_fetch_fail(self, *_):
        """Test cache keeping old values when fetch fails (content=None)."""
        cache = self.source_cache(self.url, ip={'10.0.0.1': self.now})
        entry, warning, verbose = self.run_get(
            url=self.url, cache=cache, content=None
        )
        self.assertIn('10.0.0.1', entry['ip'])
        self.assertFalse(entry['dirty'])
        warning.assert_not_called()
        verbose.assert_not_called()

    def test_url_fetch_fail_expired(self, *_):
        """Test expired cache entry removal when fetch fails."""
        cache = self.source_cache(
            self.url, ip={'10.0.0.1': self.now}, refresh=self.now - 1000
        )
        entry, warning, verbose = self.run_get(
            url=self.url, cache=cache, content=None
        )
        self.assertFalse(entry['ip'])
        self.assertTrue(entry['dirty'])
        warning.assert_not_called()
        verbose.assert_not_called()

    def test_file_source(self, *_):
        """Test local file source is read with get_file()."""
        url = './test.iplist'
        cache = self.source_cache(url, ip={'10.0.0.1': self.now})
        options = foomuuri.IPListSourceOptions()
        options.timeout = 1000
        with (
            unittest.mock.patch(
                'foomuuri.get_file', return_value='10.0.0.7\n'
            ) as get_file,
            unittest.mock.patch('foomuuri.get_url') as get_url,
            unittest.mock.patch('foomuuri.warning') as warning,
            unittest.mock.patch('foomuuri.verbose') as verbose,
        ):
            foomuuri.get_url_or_file(url, options, cache)
        entry = cache[url]
        self.assertIn('10.0.0.7', entry['ip'])
        self.assertTrue(entry['dirty'])
        get_file.assert_called_once_with(url)
        get_url.assert_not_called()
        warning.assert_not_called()
        verbose.assert_called_once_with(
            f'Iplist content for "{url}" refreshed, 1 entries'
        )

    def test_set_single_missing_ok_empty(self, *_):
        """Test warning and rc 0 for |missing-ok source with empty content."""
        cache = self.source_cache(self.url_missing_ok)
        ret, warning, fail, verbose = self.run_output(
            sources=[self.url_missing_ok],
            cache=cache,
            setname='@foo',
        )
        self.assertEqual(ret, 0)
        warning.assert_called_once_with('Iplist "@foo" is empty')
        fail.assert_not_called()
        verbose.assert_not_called()

    def test_set_single_no_missing_ok_empty(self, *_):
        """Test fail and rc 2 for source with empty content."""
        cache = self.source_cache(self.url)
        ret, warning, fail, verbose = self.run_output(
            sources=[self.url],
            cache=cache,
            setname='@foo',
        )
        self.assertEqual(ret, 2)
        fail.assert_called_once_with('Iplist "@foo" is empty', False)
        warning.assert_not_called()
        verbose.assert_not_called()

    def test_set_mixed_sources_empty(self, *_):
        """Test fail and rc 2 for mixed sources with empty content."""
        optional = self.url_missing_ok
        required = 'https://required.example/list'
        cache = self.source_cache(optional, required)
        ret, warning, fail, verbose = self.run_output(
            sources=[optional, required],
            cache=cache,
            setname='@foo',
        )
        self.assertEqual(ret, 2)
        fail.assert_called_once_with('Iplist "@foo" is empty', False)
        warning.assert_not_called()
        verbose.assert_not_called()

    def test_set_clean_soft(self, *_):
        """Test verbose skip update message with --soft (force<0)."""
        cache = self.source_cache(self.url)
        ret, warning, fail, verbose = self.run_output(
            sources=[self.url],
            cache=cache,
            setname='@foo',
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
        cache = self.source_cache(self.url, ip={'10.0.0.1': self.now})
        cache[self.url]['dirty'] = True
        ret, warning, fail, verbose = self.run_output(
            sources=[self.url],
            cache=cache,
            setname='@foo',
            force=-1,
        )
        self.assertEqual(ret, 0)
        warning.assert_not_called()
        fail.assert_not_called()
        verbose.assert_called_once_with('Updating iplist "@foo", 1 entries')

    def test_set_nonempty_updates(self, *_):
        """Test verbose update message for non-empty set."""
        cache = self.source_cache(self.url, ip={'10.0.0.1': self.now})
        ret, warning, fail, verbose = self.run_output(
            sources=[self.url],
            cache=cache,
            setname='@foo',
        )
        self.assertEqual(ret, 0)
        warning.assert_not_called()
        fail.assert_not_called()
        verbose.assert_called_once_with('Updating iplist "@foo", 1 entries')
