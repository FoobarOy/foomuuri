"""Test IPListSourceCache.write()."""
# pylint: disable=invalid-name,import-error

import unittest
import unittest.mock

import foomuuri


class TestSourceCacheWrite(unittest.TestCase):
    """Test IPListSourceCache.write()."""

    def test_write_removes_empty_entries(self):
        """Test write removes empty entries and transient metadata."""
        cache = foomuuri.IPListSourceCache(
            {
                'https://foo.bar/empty.txt': {
                    'ip': {},
                    'dirty': True,
                    'refresh': 100,
                },
                'https://foo.bar/empty.txt|missing-ok': {
                    'ip': {},
                    'dirty': True,
                    'refresh': 100,
                },
                'manual.@empty': {
                    'ip': {},
                    'dirty': True,
                    'refresh': 100,
                },
                'https://foo.bar/list.txt': {
                    'ip': {'10.0.0.1': 200},
                    'dirty': True,
                    'refresh': 100,
                },
                'manual.@source': {
                    'ip': {'10.0.0.2': 300},
                    'dirty': True,
                    'refresh': 100,
                },
            }
        )

        written_cache = {
            'https://foo.bar/empty.txt|missing-ok': {'ip': {}, 'refresh': 100},
            'https://foo.bar/list.txt': {
                'ip': {'10.0.0.1': 200},
                'refresh': 100,
            },
            'manual.@source': {'ip': {'10.0.0.2': 300}},
        }
        filename = unittest.mock.Mock()

        with (
            unittest.mock.patch('foomuuri.state_file', return_value=filename),
            unittest.mock.patch('foomuuri.save_file') as save_file,
        ):
            cache.write()

        self.assertEqual(
            cache,
            written_cache,
        )
        save_file.assert_called_once_with(
            filename,
            written_cache,
        )
