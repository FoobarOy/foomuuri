"""Test IPListCache.build_iplist()."""

# pylint: disable=invalid-name,import-error

import time
import unittest

import foomuuri


class TestIPListCacheBuild(unittest.TestCase):
    """Test IPListCache.build_iplist()."""

    def setUp(self):
        """Prepare test fixtures."""
        self.now = int(time.time())

    def test_static_addresses(self):
        """Test static address sources use permanent expiration."""
        cache = foomuuri.IPListCache()

        cache.build_iplist('@foo', ['10.0.0.1', '2001:db8::1'], self.now)

        self.assertEqual(
            cache['@foo'],
            {
                'ip': {
                    '10.0.0.1': foomuuri.IPListCache.expire_forever,
                    '2001:db8::1': foomuuri.IPListCache.expire_forever,
                },
                'dirty': True,
                'refresh': self.now,
            },
        )

    def test_rebuilds_and_merges_sources(self):
        """Test rebuilding and merging cached and manual sources.

        Iplist's existing addresses are overwritten.
        """
        cache = foomuuri.IPListCache(
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

        cache.build_iplist('@foo', ['foo.example', '10.0.0.1'], self.now)

        self.assertEqual(
            cache['@foo'],
            {
                'ip': {
                    '10.0.0.1': foomuuri.IPListCache.expire_forever,
                    '192.0.2.1': 300,
                    '2001:db8::2': 400,
                },
                'dirty': True,
                'refresh': self.now,
            },
        )
