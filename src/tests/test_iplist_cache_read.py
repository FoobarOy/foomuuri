"""Test IPListCache.read()."""

# pylint: disable=invalid-name,import-error

import json
import unittest.mock

import foomuuri


class TestIPListCacheRead(unittest.TestCase):
    """Test IPListCache.read()."""

    def test_ignore_removed_entries(self):
        """Test ignore unknown cache entries."""
        data = {
            '@unknown': {
                'ip': {'10.0.0.1': foomuuri.IPListCache.expire_forever},
            },
            'manual.@unknown': {
                'ip': {'10.0.0.2': foomuuri.IPListCache.expire_forever},
            },
            'broken': {'dirty': False},
            '@known': {
                'ip': {'10.0.0.3': foomuuri.IPListCache.expire_forever},
                'refresh': 1,
            },
        }
        filename = unittest.mock.Mock()
        filename.read_text.return_value = json.dumps(data)

        with (
            unittest.mock.patch('foomuuri.state_file', return_value=filename),
            unittest.mock.patch('foomuuri.verbose'),
        ):
            cache = foomuuri.IPListCache.read({'@known'})

        self.assertEqual(set(cache), {'@known'})
        self.assertEqual(cache['@known'], data['@known'])
