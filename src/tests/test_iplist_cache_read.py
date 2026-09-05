"""Test IPListSourceCache.read()."""

# pylint: disable=invalid-name,import-error

import json
import unittest.mock

import foomuuri


class TestIPListSourceCacheRead(unittest.TestCase):
    """Test IPListSourceCache.read()."""

    def test_read_removes_entries(self):
        """Test read removes unknown, broken, and empty cache entries."""
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

        with (
            unittest.mock.patch('foomuuri.state_file', return_value=filename),
            unittest.mock.patch('foomuuri.verbose'),
        ):
            cache = foomuuri.IPListSourceCache.read({'@known'})

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
