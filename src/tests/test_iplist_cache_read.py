"""Test IPListSourceCache.read()."""

# pylint: disable=invalid-name,import-error

import json
import time
import unittest.mock

import foomuuri


class TestIPListSourceCacheRead(unittest.TestCase):
    """Test IPListSourceCache.read()."""

    def setUp(self):
        """Define common cache read data."""
        self.filename = unittest.mock.Mock()
        self.now = int(time.time())
        self.iplists = foomuuri.IPLists()
        self.iplists['@known'] = foomuuri.IPList()

    def _read(self, data, sources):
        """Read cache using common fixtures helper."""
        self.filename.read_text.return_value = json.dumps(data)
        self.iplists['@known'].sources = sources
        with (
            unittest.mock.patch(
                'foomuuri.state_file', return_value=self.filename
            ),
            unittest.mock.patch('foomuuri.verbose') as verbose,
        ):
            cache = foomuuri.IPListSourceCache.read(self.iplists)
        return cache, verbose

    def test_cache_read_prunes_sources(self):
        """Test cache read removes legacy and unconfigured sources."""
        data = {
            '@unknown': {
                'ip': {'10.0.0.1': foomuuri.IPListSourceCache.expire_never},
            },
            'manual.@unknown': {
                'ip': {'10.0.0.2': foomuuri.IPListSourceCache.expire_never},
            },
            'manual.@known': {
                'ip': {'10.0.0.4': foomuuri.IPListSourceCache.expire_never},
                'refresh': 1,
            },
            'broken': {'dirty': False},
            '@known': {
                'ip': {'10.0.0.3': foomuuri.IPListSourceCache.expire_never},
                'refresh': 1,
            },
            'https://foo.bar/removed.txt': {
                'ip': {'10.0.0.9': foomuuri.IPListSourceCache.expire_never},
                'refresh': 100,
            },
            'https://foo.bar/empty.txt': {
                'ip': {},
                'refresh': 100,
            },
            'manual.@empty': {
                'ip': {},
                'refresh': 100,
            },
            'https://foo.bar/empty.txt|missing-ok': {
                'ip': {},
                'refresh': 100,
            },
            'https://foo.bar/list.txt|missing-ok': {
                'ip': {'10.0.0.1': foomuuri.IPListSourceCache.expire_never},
                'refresh': 100,
            },
        }
        cache, verbose = self._read(
            data,
            [
                'https://foo.bar/empty.txt',
                'https://foo.bar/empty.txt|missing-ok',
                'https://foo.bar/list.txt|missing-ok',
            ],
        )
        verbose.assert_has_calls(
            [
                unittest.mock.call(
                    'Deleting legacy iplist "@unknown" from cache'
                ),
                unittest.mock.call(
                    'Deleting source "manual.@unknown" from cache, '
                    'not in config'
                ),
                unittest.mock.call(
                    'Deleting source "broken" from cache, not in config'
                ),
                unittest.mock.call(
                    'Deleting legacy iplist "@known" from cache'
                ),
                unittest.mock.call(
                    'Deleting source "https://foo.bar/removed.txt" '
                    'from cache, not in config',
                ),
                unittest.mock.call(
                    'Deleting source "manual.@empty" from cache, '
                    'not in config',
                ),
            ]
        )
        self.assertEqual(verbose.call_count, 6)

        self.assertEqual(
            cache,
            {
                'manual.@known': {
                    'ip': {
                        '10.0.0.4': foomuuri.IPListSourceCache.expire_never
                    },
                    'refresh': 1,
                },
                'https://foo.bar/empty.txt|missing-ok': {
                    'ip': {},
                    'refresh': 100,
                },
                'https://foo.bar/list.txt|missing-ok': {
                    'ip': {
                        '10.0.0.1': foomuuri.IPListSourceCache.expire_never
                    },
                    'refresh': 100,
                },
            },
        )

    def test_cache_read_removes_expired_addresses(self):
        """Test cache read removes expired addresses."""
        data = {
            'https://foo.bar/list.txt': {
                'ip': {
                    '10.0.0.1': 0,
                    '10.0.0.2': self.now,
                    '10.0.0.3': self.now + 3600,
                },
                'refresh': 1,
            },
            'https://foo.bar/empty.txt|missing-ok': {
                'ip': {'10.0.0.4': 0},
                'refresh': 1,
            },
        }
        cache, verbose = self._read(
            data,
            [
                'https://foo.bar/list.txt',
                'https://foo.bar/empty.txt|missing-ok',
            ],
        )
        verbose.assert_has_calls(
            [
                unittest.mock.call(
                    'Deleting expired iplist "https://foo.bar/list.txt" '
                    'entry "10.0.0.1"'
                ),
                unittest.mock.call(
                    'Deleting expired iplist "https://foo.bar/list.txt" '
                    'entry "10.0.0.2"'
                ),
                unittest.mock.call(
                    'Deleting expired iplist '
                    '"https://foo.bar/empty.txt|missing-ok" '
                    'entry "10.0.0.4"'
                ),
            ]
        )
        self.assertEqual(verbose.call_count, 3)
        self.assertEqual(
            cache,
            {
                'https://foo.bar/list.txt': {
                    'ip': {'10.0.0.3': self.now + 3600},
                    'refresh': 1,
                },
                'https://foo.bar/empty.txt|missing-ok': {
                    'ip': {},
                    'refresh': 1,
                },
            },
        )

    def test_cache_read_removes_empty_sources(self):
        """Test cache read removes empty sources without |missing-ok."""
        data = {
            'https://foo.bar/empty.txt': {
                'ip': {},
                'refresh': 1,
            },
            'https://foo.bar/empty.txt|missing-ok': {
                'ip': {},
                'refresh': 1,
            },
            'manual.@known': {
                'ip': {},
                'refresh': 1,
            },
            'https://foo.bar/list.txt': {
                'ip': {
                    '10.0.0.1': self.now + 3600,
                },
                'refresh': 1,
            },
        }
        cache, verbose = self._read(
            data,
            [
                'https://foo.bar/empty.txt',
                'https://foo.bar/empty.txt|missing-ok',
                'https://foo.bar/list.txt',
            ],
        )
        verbose.assert_not_called()
        self.assertEqual(
            cache,
            {
                'https://foo.bar/empty.txt|missing-ok': {
                    'ip': {},
                    'refresh': 1,
                },
                'https://foo.bar/list.txt': {
                    'ip': {'10.0.0.1': self.now + 3600},
                    'refresh': 1,
                },
            },
        )
