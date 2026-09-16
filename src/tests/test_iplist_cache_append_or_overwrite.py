"""Test IPListSourceCache._append_or_overwrite()."""
# pylint: disable=invalid-name,import-error

import time
import unittest

import foomuuri

from src.tests.test_iplist_cache_refresh import source_cache


class TestAppendOrOverwrite(unittest.TestCase):
    """Test IPListSourceCache._append_or_overwrite()."""

    def setUp(self):
        """Prepare test fixtures."""
        self.now = int(time.time())
        self.expire = self.now + 1000
        self.source = 'https://foo.bar/iplist'

    def run_append_or_overwrite(
        self,
        cache,
        addresses,
        overwrite=None,
        default_is_overwrite=True,
    ):
        """Call _append_or_overwrite() with common fixtures."""
        options = foomuuri.IPListSourceOptions()
        options.overwrite = overwrite
        # pylint: disable=protected-access
        # ruff: ignore[private-member-access]
        cache._append_or_overwrite(
            self.source, addresses, options, default_is_overwrite, self.now
        )
        return cache[self.source]

    def cached_cache(self):
        """Return cache with one cached address for self.source."""
        return source_cache(
            self.source, ip={'10.0.0.1': self.now}, refresh=self.now
        )

    def test_default_overwrite_replaces(self, *_):
        """Test default overwrite mode replaces cached addresses."""
        cache = self.cached_cache()
        entry = self.run_append_or_overwrite(
            cache, {'10.0.0.9': self.expire}, default_is_overwrite=True
        )
        self.assertEqual(entry['ip'], {'10.0.0.9': self.expire})

    def test_default_append_merges(self, *_):
        """Test default append mode merges addresses to cached ones."""
        cache = self.cached_cache()
        entry = self.run_append_or_overwrite(
            cache, {'10.0.0.9': self.expire}, default_is_overwrite=False
        )
        self.assertEqual(
            entry['ip'], {'10.0.0.1': self.now, '10.0.0.9': self.expire}
        )

    def test_overwrite_true_overrides_append_default(self, *_):
        """Test overwrite=yes replaces despite append default."""
        cache = self.cached_cache()
        entry = self.run_append_or_overwrite(
            cache,
            {'10.0.0.9': self.expire},
            overwrite=True,
            default_is_overwrite=False,
        )
        self.assertEqual(entry['ip'], {'10.0.0.9': self.expire})

    def test_overwrite_false_overrides_overwrite_default(self, *_):
        """Test overwrite=no appends despite overwrite default."""
        cache = self.cached_cache()
        entry = self.run_append_or_overwrite(
            cache,
            {'10.0.0.9': self.expire},
            overwrite=False,
            default_is_overwrite=True,
        )
        self.assertEqual(
            entry['ip'], {'10.0.0.1': self.now, '10.0.0.9': self.expire}
        )

    def test_marks_dirty_and_refresh(self):
        """Test entry is marked dirty and stamped with refresh time."""
        cache = self.cached_cache()
        entry = self.run_append_or_overwrite(cache, {'10.0.0.9': self.expire})
        self.assertTrue(entry['dirty'])
        self.assertEqual(entry['refresh'], self.now)

    def test_creates_missing_entry(self):
        """Test missing source entry is created."""
        cache = foomuuri.IPListSourceCache()
        entry = self.run_append_or_overwrite(cache, {'10.0.0.9': self.expire})
        self.assertEqual(entry['ip'], {'10.0.0.9': self.expire})
        self.assertTrue(entry['dirty'])
        self.assertEqual(entry['refresh'], self.now)
