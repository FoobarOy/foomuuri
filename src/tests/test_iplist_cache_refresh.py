"""Test IPListSourceCache operations."""
# pylint: disable=invalid-name,import-error

import copy
import time
import unittest.mock

import foomuuri
from foomuuri import INTERNAL as BASE_INTERNAL


def source_cache(*sources, ip=None, refresh=None):
    """Return source cache with one entry per source."""
    entry = {'ip': {} if ip is None else ip, 'dirty': False}
    if refresh is not None:
        entry['refresh'] = refresh
    return foomuuri.IPListSourceCache(
        {source: copy.deepcopy(entry) for source in sources}
    )


@unittest.mock.patch(
    'foomuuri.INTERNAL', new_callable=lambda: copy.deepcopy(BASE_INTERNAL)
)
class TestSourceCacheRefreshURLOrFile(unittest.TestCase):
    """Test IPListSourceCache.refresh_url_or_file()."""

    def setUp(self):
        """Prepare test fixtures."""
        self.now = int(time.time())
        self.url = 'https://foo.bar/iplist'
        self.url_missing_ok = f'{self.url}|missing-ok'

    @staticmethod
    def run_refresh(source, cache, content, force=0):
        """Call IPListSourceCache.refresh_url_or_file()."""
        foomuuri.INTERNAL.force = force
        options = foomuuri.IPListSourceOptions()
        options.timeout = 1000
        options.refresh = 1000
        with (
            unittest.mock.patch('foomuuri.get_url', return_value=content),
            unittest.mock.patch('foomuuri.warning') as warning,
            unittest.mock.patch('foomuuri.verbose') as verbose,
        ):
            cache.refresh_url_or_file(source, options)
        return cache.get(source), warning, verbose

    def test_empty_url_missing_ok(self, *_):
        """Test no warning for empty source with |missing-ok."""
        cache = source_cache(
            self.url_missing_ok, ip={'10.0.0.1': self.now}, refresh=self.now
        )
        entry, warning, verbose = self.run_refresh(
            source=self.url_missing_ok, cache=cache, content=''
        )
        self.assertFalse(entry['ip'])
        self.assertTrue(entry['dirty'])
        warning.assert_not_called()
        verbose.assert_called_once_with(
            f'Iplist content for "{self.url_missing_ok}" refreshed, 0 entries'
        )

    def test_empty_url_no_missing_ok(self, *_):
        """Test warning for empty source without |missing-ok."""
        cache = source_cache(self.url, ip={'10.0.0.1': self.now})
        entry, warning, verbose = self.run_refresh(
            source=self.url, cache=cache, content=''
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
        cache = source_cache(self.url, ip={'10.0.0.1': self.now})
        entry, warning, verbose = self.run_refresh(
            source=self.url, cache=cache, content='10.0.0.9\n'
        )
        self.assertIn('10.0.0.9', entry['ip'])
        self.assertTrue(entry['dirty'])
        warning.assert_not_called()
        verbose.assert_called_once_with(
            f'Iplist content for "{self.url}" refreshed, 1 entries'
        )

    def test_url_cached_soft(self, *_):
        """Test using cache values with --soft (force<0)."""
        cache = source_cache(
            self.url, ip={'10.0.0.1': self.now}, refresh=self.now
        )
        entry, warning, verbose = self.run_refresh(
            source=self.url, cache=cache, content='10.0.0.9\n', force=-1
        )
        self.assertIn('10.0.0.1', entry['ip'])
        self.assertFalse(entry['dirty'])
        warning.assert_not_called()
        verbose.assert_called_once_with(f'Using cached value for "{self.url}"')

    def test_url_fetch_fail(self, *_):
        """Test cache keeping old values when fetch fails."""
        cache = source_cache(self.url, ip={'10.0.0.1': self.now})
        entry, warning, verbose = self.run_refresh(
            source=self.url, cache=cache, content=None
        )
        self.assertIn('10.0.0.1', entry['ip'])
        self.assertFalse(entry['dirty'])
        warning.assert_not_called()
        verbose.assert_not_called()

    def test_url_fetch_fail_expired(self, *_):
        """Test expired cache entry removal when fetch fails."""
        cache = source_cache(
            self.url, ip={'10.0.0.1': self.now}, refresh=self.now - 1000
        )
        entry, warning, verbose = self.run_refresh(
            source=self.url, cache=cache, content=None
        )
        self.assertFalse(entry['ip'])
        self.assertTrue(entry['dirty'])
        warning.assert_not_called()
        verbose.assert_not_called()

    def test_file_source(self, *_):
        """Test local file source is read with get_file()."""
        file_path = './test.iplist'
        cache = source_cache(file_path, ip={'10.0.0.1': self.now})
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
            cache.refresh_url_or_file(file_path, options)
        entry = cache[file_path]
        self.assertIn('10.0.0.7', entry['ip'])
        self.assertTrue(entry['dirty'])
        get_file.assert_called_once_with(file_path)
        get_url.assert_not_called()
        warning.assert_not_called()
        verbose.assert_called_once_with(
            f'Iplist content for "{file_path}" refreshed, 1 entries'
        )
