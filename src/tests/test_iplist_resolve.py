"""Test iplist resolve_all_hostnames().

Cover hostname resolution, iplist cache management and user interaction
behaviour.
"""
# pylint: disable=invalid-name,import-error

import copy
import time
import unittest.mock

import foomuuri
from foomuuri import INTERNAL as BASE_INTERNAL


@unittest.mock.patch(
    'foomuuri.INTERNAL', new_callable=lambda: copy.deepcopy(BASE_INTERNAL)
)
class TestResolveHostnames(unittest.TestCase):
    """Test resolve_all_hostnames() behaviour."""

    def setUp(self):
        """Prepare test fixtures."""
        self.now = int(time.time())

    @staticmethod
    def source_options(timeout=1000):
        """Return IPListSourceOptions instance."""
        options = foomuuri.IPListSourceOptions()
        options.timeout = timeout
        return options

    @staticmethod
    def run_resolve(resolve, cache, addresses=None, force=0):
        """Call resolve_all_hostnames() with mocked helpers."""
        # addresses: dict, hostname -> set of resolved IPs
        if addresses is None:
            addresses = {}
        foomuuri.INTERNAL.force = force
        with (
            unittest.mock.patch(
                'foomuuri.resolve_one_hostname',
                side_effect=lambda name: addresses.get(name, set()),
            ),
            unittest.mock.patch('foomuuri.warning') as warning,
            unittest.mock.patch('foomuuri.verbose') as verbose,
        ):
            foomuuri.resolve_all_hostnames(resolve, cache)
        return cache, warning, verbose

    def test_resolve_hostname_ok(self, *_):
        """Test hostname resolution and IP address caching."""
        cache, warning, verbose = self.run_resolve(
            {'foo.bar': self.source_options()},
            cache={},
            addresses={'foo.bar': {'10.0.0.5'}},
        )
        entry = cache['foo.bar']
        self.assertEqual(entry['ip']['10.0.0.5'], entry['refresh'] + 1000)
        self.assertTrue(entry['dirty'])
        warning.assert_not_called()
        verbose.assert_any_call('Hostname "foo.bar" resolved to: 10.0.0.5')

    def test_resolve_hostname_expire_forever(self, *_):
        """Test very large timeout sets expiry to "forever"."""
        cache, _, _ = self.run_resolve(
            {'foo.bar': self.source_options(foomuuri.INTERNAL.expire_max + 1)},
            cache={},
            addresses={'foo.bar': {'10.0.0.9'}},
        )
        self.assertEqual(
            cache['foo.bar']['ip']['10.0.0.9'],
            foomuuri.INTERNAL.expire_forever,
        )

    def test_resolve_hostname_failed_warns(self, *_):
        """Test warning when hostname resolves to nothing."""
        cache, warning, _ = self.run_resolve(
            {'foo.bar': self.source_options()}, cache={}
        )
        self.assertNotIn('foo.bar', cache)
        warning.assert_called_once_with(
            'No IP address found for hostname "foo.bar" in iplist'
        )

    def test_resolve_hostname_failed_missing_ok(self, *_):
        """Test no warning when |missing-ok hostname resolves to nothing."""
        cache, warning, _ = self.run_resolve(
            {'foo.bar|missing-ok': self.source_options()}, cache={}
        )
        self.assertNotIn('foo.bar|missing-ok', cache)
        warning.assert_not_called()

    def test_resolve_hostname_appends(self, *_):
        """Test hostname resolution appends IP addresses to cache."""
        cache = {
            'foo.bar|missing-ok': {
                'ip': {'10.0.0.1': 0},
                'dirty': False,
                'refresh': self.now,
            }
        }
        cache, _, _ = self.run_resolve(
            {'foo.bar|missing-ok': self.source_options()},
            cache=cache,
            addresses={'foo.bar|missing-ok': {'10.0.0.9'}},
        )
        self.assertIn('10.0.0.1', cache['foo.bar|missing-ok']['ip'])
        self.assertIn('10.0.0.9', cache['foo.bar|missing-ok']['ip'])
        self.assertTrue(cache['foo.bar|missing-ok']['dirty'])

    def test_resolve_hostname_expired_cleared(self, *_):
        """Test resolution clears expired cached IP addresses."""
        cache = {
            'foo.bar': {
                'ip': {'10.0.0.1': 0},
                'dirty': False,
                'refresh': self.now - 2000,
            }
        }
        cache, _, _ = self.run_resolve(
            {'foo.bar': self.source_options(timeout=1000)},
            cache=cache,
            addresses={'foo.bar': {'10.0.0.9'}},
        )
        self.assertNotIn('10.0.0.1', cache['foo.bar']['ip'])
        self.assertIn('10.0.0.9', cache['foo.bar']['ip'])

    def test_resolve_hostname_expired_soft_reresolves(self, *_):
        """Test --soft (force<0) mode re-resolves expired cache entry."""
        cache = {
            'foo.bar': {
                'ip': {'10.0.0.1': 0},
                'dirty': False,
                'refresh': self.now - 2000,
            }
        }
        cache, warning, verbose = self.run_resolve(
            {'foo.bar': self.source_options(timeout=1000)},
            cache=cache,
            addresses={'foo.bar': {'10.0.0.9'}},
            force=-1,
        )
        self.assertNotIn('10.0.0.1', cache['foo.bar']['ip'])
        self.assertIn('10.0.0.9', cache['foo.bar']['ip'])
        warning.assert_not_called()
        verbose.assert_any_call('Hostname "foo.bar" resolved to: 10.0.0.9')

    def test_resolve_hostname_cached_soft(self, *_):
        """Test no resolution with fresh cache and --soft (force<0)."""
        cache = {
            'foo.bar|missing-ok': {
                'ip': {'10.0.0.1': 0},
                'dirty': False,
                'refresh': self.now,
            }
        }
        cache, warning, verbose = self.run_resolve(
            {'foo.bar|missing-ok': self.source_options()},
            cache=cache,
            addresses={'foo.bar|missing-ok': {'10.0.0.9'}},
            force=-1,
        )
        self.assertEqual(cache['foo.bar|missing-ok']['ip'], {'10.0.0.1': 0})
        verbose.assert_called_once_with('Using cached value for "foo.bar"')
        warning.assert_not_called()

    def test_resolve_hostnames_all_cached_no_lookup(self, *_):
        """Test no resolution when all hostnames cached in soft mode."""
        names = ('foo.bar', 'baz.qux')
        cache = {
            name: {
                'ip': {'10.0.0.1': 0},
                'dirty': False,
                'refresh': self.now,
            }
            for name in names
        }
        snapshot = copy.deepcopy(cache)
        cache, warning, verbose = self.run_resolve(
            {name: self.source_options() for name in names},
            cache=cache,
            addresses={name: {'10.0.0.9'} for name in names},
            force=-1,
        )
        self.assertEqual(cache, snapshot)
        warning.assert_not_called()
        for call in verbose.call_args_list:
            self.assertNotIn('DNS lookup for:', call.args[0])
