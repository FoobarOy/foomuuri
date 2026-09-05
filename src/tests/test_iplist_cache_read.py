"""Test IPListSourceCache.read()."""

# pylint: disable=invalid-name,import-error

import json
import unittest.mock

import foomuuri


class TestIPListSourceCacheRead(unittest.TestCase):
    """Test IPListSourceCache.read()."""

    def test_read_removes_entries(self):
        """Test read removes legacy, broken, and unconfigured entries."""
        data = {
            '@unknown': {
                'ip': {'10.0.0.1': foomuuri.IPListSourceCache.expire_forever},
            },
            'manual.@unknown': {
                'ip': {'10.0.0.2': foomuuri.IPListSourceCache.expire_forever},
            },
            'manual.@known': {
                'ip': {'10.0.0.4': foomuuri.IPListSourceCache.expire_forever},
                'refresh': 1,
            },
            'broken': {'dirty': False},
            '@known': {
                'ip': {'10.0.0.3': foomuuri.IPListSourceCache.expire_forever},
                'refresh': 1,
            },
            'https://foo.bar/removed.txt': {
                'ip': {'10.0.0.9': foomuuri.IPListSourceCache.expire_forever},
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
                'ip': {'10.0.0.1': foomuuri.IPListSourceCache.expire_forever},
                'refresh': 100,
            },
        }
        filename = unittest.mock.Mock()
        filename.read_text.return_value = json.dumps(data)

        iplists = foomuuri.IPLists()
        iplists['@known'] = foomuuri.IPList(
            sources=[
                'https://foo.bar/empty.txt',
                'https://foo.bar/empty.txt|missing-ok',
                'https://foo.bar/list.txt|missing-ok',
            ]
        )

        with (
            unittest.mock.patch('foomuuri.state_file', return_value=filename),
            unittest.mock.patch('foomuuri.verbose') as verbose,
        ):
            cache = foomuuri.IPListSourceCache.read(iplists)

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
                        '10.0.0.4': foomuuri.IPListSourceCache.expire_forever
                    },
                    'refresh': 1,
                },
                'https://foo.bar/empty.txt|missing-ok': {
                    'ip': {},
                    'refresh': 100,
                },
                'https://foo.bar/list.txt|missing-ok': {
                    'ip': {
                        '10.0.0.1': foomuuri.IPListSourceCache.expire_forever
                    },
                    'refresh': 100,
                },
            },
        )
