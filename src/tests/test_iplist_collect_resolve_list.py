"""Test iplist_collect_resolve_list()."""
# pylint: disable=invalid-name,import-error

import unittest

from foomuuri import (
    IPList,
    IPListOptions,
    IPLists,
    iplist_collect_resolve_list,
)


class TestIPListCollectResolveList(unittest.TestCase):
    """Test iplist_collect_resolve_list()."""

    @staticmethod
    def _iplist(sources, refs, **kwargs):
        """Return IPList with sources and source references."""
        options = IPListOptions()
        for name, value in kwargs.items():
            setattr(options, name, value)

        return IPList(
            options=options,
            sources=sources,
            source_refs=refs,
        )

    def test_unset_options_resets_to_default(self):
        """Test unset source option resets to default."""
        iplists = IPLists()
        iplists['@a'] = self._iplist(
            ['https://foo'],
            {'https://foo': 'line1'},
            url_timeout=100,
            url_max_size=256,
        )
        iplists['@b'] = self._iplist(
            ['https://foo'],
            {'https://foo': 'line2'},
            url_refresh=20,
        )
        locations, _ = iplist_collect_resolve_list(iplists, {'@a'})
        source_options = locations['https://foo']
        self.assertEqual(source_options.timeout, IPListOptions.url_timeout)
        self.assertEqual(source_options.max_size, IPListOptions.url_max_size)
        self.assertEqual(source_options.refresh, 20)

    def test_url_source_options(self):
        """Test all URL source options."""
        iplists = IPLists()
        iplists['@a'] = self._iplist(
            ['https://foo'],
            {'https://foo': 'line1'},
            url_timeout=100,
            url_refresh=10,
            url_max_size=1000,
            overwrite=True,
            missing_ok=True,
        )
        iplists['@b'] = self._iplist(
            ['https://foo'],
            {'https://foo': 'line2'},
            url_timeout=200,
            url_refresh=20,
            url_max_size=2000,
            overwrite=False,
            missing_ok=False,
        )
        locations, _ = iplist_collect_resolve_list(iplists, {'@a'})
        source_options = locations['https://foo']
        self.assertEqual(source_options.timeout, 200)
        self.assertEqual(source_options.refresh, 20)
        self.assertEqual(source_options.max_size, 2000)
        self.assertFalse(source_options.overwrite)
        self.assertFalse(source_options.missing_ok)

    def test_hostname_source_options(self):
        """Test all hostname source options.."""
        iplists = IPLists()
        iplists['@a'] = self._iplist(
            ['foo.bar'],
            {'foo.bar': 'line1'},
            dns_timeout=100,
            dns_refresh=10,
            overwrite=True,
            missing_ok=True,
        )
        iplists['@b'] = self._iplist(
            ['foo.bar'],
            {'foo.bar': 'line2'},
            dns_timeout=200,
            dns_refresh=20,
            overwrite=False,
            missing_ok=False,
        )
        _, hostnames = iplist_collect_resolve_list(iplists, {'@a'})
        source_options = hostnames['foo.bar']
        self.assertEqual(source_options.timeout, 200)
        self.assertEqual(source_options.refresh, 20)
        self.assertFalse(source_options.overwrite)
        self.assertFalse(source_options.missing_ok)

    def test_static_source_excluded(self):
        """Test static IP source is not returned as location or hostname."""
        iplists = IPLists()
        iplists['@a'] = self._iplist(['10.0.0.1'], {'10.0.0.1': 'line1'})
        locations, hostnames = iplist_collect_resolve_list(iplists, {'@a'})
        self.assertFalse(locations)
        self.assertFalse(hostnames)

    def test_iplists_from_update_only(self):
        """Test that only iplists from update_only are processed."""
        iplists = IPLists()
        iplists['@a'] = self._iplist(['https://foo'], {'https://foo': 'line1'})
        iplists['@b'] = self._iplist(['https://bar'], {'https://bar': 'line2'})
        locations, _ = iplist_collect_resolve_list(iplists, {'@a'})
        self.assertEqual(set(locations), {'https://foo'})
