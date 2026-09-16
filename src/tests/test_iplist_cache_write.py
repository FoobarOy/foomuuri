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
                'https://foo.bar/empty2.txt': {
                    'ip': {},
                    'dirty': True,
                    'refresh': 100,
                },
                'https://foo.bar/keep.txt': {
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
            'https://foo.bar/keep.txt': {'ip': {}, 'refresh': 100},
            'https://foo.bar/list.txt': {
                'ip': {'10.0.0.1': 200},
                'refresh': 100,
            },
            'manual.@source': {'ip': {'10.0.0.2': 300}},
        }
        filename = unittest.mock.Mock()

        iplists = foomuuri.IPLists()
        iplists['@missingok'] = foomuuri.IPList(
            options=foomuuri.IPListOptions(missing_ok=True),
            sources=['https://foo.bar/keep.txt'],
        )
        iplists['@remove'] = foomuuri.IPList(
            options=foomuuri.IPListOptions(missing_ok=False),
            sources=['https://foo.bar/empty.txt'],
        )
        iplists['@remove2'] = foomuuri.IPList(
            options=foomuuri.IPListOptions(missing_ok=None),
            sources=['https://foo.bar/empty2.txt'],
        )
        with (
            unittest.mock.patch('foomuuri.state_file', return_value=filename),
            unittest.mock.patch('foomuuri.save_file') as save_file,
        ):
            cache.write(iplists)

        self.assertEqual(
            cache,
            written_cache,
        )
        save_file.assert_called_once_with(
            filename,
            written_cache,
        )
