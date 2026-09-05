"""Test IPListValue.from_sources()."""

# pylint: disable=invalid-name,import-error

import copy
import unittest

import foomuuri


class TestIPListValueBuild(unittest.TestCase):
    """Test IPListValue.from_sources()."""

    def test_static_addresses(self):
        """Test static address sources use permanent expiration."""
        source_cache = foomuuri.IPListSourceCache()

        iplist = foomuuri.IPListValue.from_sources(
            source_cache, '@foo', ['10.0.0.1', '2001:db8::1']
        )

        self.assertEqual(
            iplist.addresses,
            {
                '10.0.0.1': foomuuri.IPListSourceCache.expire_forever,
                '2001:db8::1': foomuuri.IPListSourceCache.expire_forever,
            },
        )
        self.assertTrue(iplist.dirty)
        self.assertEqual(dict(source_cache), {})

    def test_rebuilds_and_merges_sources(self):
        """Test rebuilding an iplist from cached and manual sources.

        Existing transient iplist addresses are not read or overwritten.
        """
        source_cache = foomuuri.IPListSourceCache(
            {
                '@foo': {
                    'ip': {'192.0.2.99': 456},
                    'dirty': False,
                    'refresh': 100,
                },
                'foo.example': {
                    'ip': {
                        '10.0.0.1': 200,
                        '192.0.2.1': 250,
                    },
                    'dirty': True,
                    'refresh': 100,
                },
                'manual.@foo': {
                    'ip': {
                        '192.0.2.1': 300,
                        '2001:db8::2': 400,
                    },
                    'dirty': True,
                    'refresh': 100,
                },
            }
        )
        snapshot = copy.deepcopy(source_cache)

        iplist = foomuuri.IPListValue.from_sources(
            source_cache, '@foo', ['foo.example', '10.0.0.1']
        )

        self.assertEqual(
            iplist.addresses,
            {
                '10.0.0.1': foomuuri.IPListSourceCache.expire_forever,
                '192.0.2.1': 300,
                '2001:db8::2': 400,
            },
        )
        self.assertTrue(iplist.dirty)
        self.assertEqual(source_cache, snapshot)
