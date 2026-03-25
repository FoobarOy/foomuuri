"""Basic unit tests of parse_config_iplist()."""
# pylint: disable=invalid-name,import-error
# ruff: noqa: N803

import contextlib
import copy
import unittest
import unittest.mock

from foomuuri import CONFIG as BASE_CONFIG
from foomuuri import INTERNAL as BASE_INTERNAL
from foomuuri import (
    IPListOptions,
    minimal_config,
    parse_config_iplist,
    parse_duration,
)


@unittest.mock.patch(
    'foomuuri.INTERNAL', new_callable=lambda: copy.deepcopy(BASE_INTERNAL)
)
@unittest.mock.patch(
    'foomuuri.CONFIG', new_callable=lambda: copy.deepcopy(BASE_CONFIG)
)
class TestIplistParseConfig(unittest.TestCase):
    """Test parse_config_iplist()."""
    @staticmethod
    @contextlib.contextmanager
    def mock_config_foomuuri(section: str = 'iplist', content: str = ''):
        """Return context manager of foomuuri.find_config_files() patch.

        foomuuri.find_config_files() is patched to return generated
        foomuuri configuration file, containing arbitrary section {}
        with specified content."""
        # consult tests/test_parse_config_foomuuri.py for mock explanation
        config_file = unittest.mock.MagicMock()
        config_file.read_text.return_value = f"""
            {section} {{
                {content}
            }}
        """
        with unittest.mock.patch(
            'foomuuri.find_config_files', side_effect=[[], [config_file]]
        ):
            yield config_file

    @unittest.mock.patch('foomuuri.warning')
    def test_obsolete_syntax(self, warning, *_):
        """Test obsolete resolve{} section and timeout/refresh options."""
        with self.mock_config_foomuuri(section='resolve', content="""
            timeout 1d 5m
            refresh 0d 30m
            @foo https://foob.ar/
        """) as config_file:
            iplists = parse_config_iplist(minimal_config())
            options = iplists['@foo'].options
            self.assertEqual(options.dns_timeout, parse_duration('1d 5m', 0))
            self.assertEqual(options.url_timeout, parse_duration('1d 5m', 0))
            self.assertEqual(options.dns_refresh, parse_duration('0d 30m', 0))
            self.assertEqual(options.url_refresh, parse_duration('0d 30m', 0))
            self.assertEqual(iplists['@foo'].sources, ['https://foob.ar/'])
            warning.assert_has_calls([
                unittest.mock.call(
                    'Section "resolve" is obsolete, use "iplist" instead',
                ),
                unittest.mock.call(
                    f'File {config_file} line 4: Iplist "timeout" is obsolete,'
                    ' use "dns_timeout" or "url_timeout" instead',
                ),
                unittest.mock.call(
                    f'File {config_file} line 5: Iplist "refresh" is obsolete,'
                    ' use "dns_refresh" or "url_refresh" instead',
                ),
            ])

    def test_empty_iplist_definition(self, *_):
        """Test empty iplist definition."""
        with self.mock_config_foomuuri(section='iplist', content="""
            @foo
            @foo -
        """):
            iplists = parse_config_iplist(minimal_config())
            self.assertEqual(iplists['@foo'].sources, [])

    def test_single_line_multiple_valid_default_options(self, *_):
        """Test multple valid default options on single line."""
        with self.mock_config_foomuuri(section='iplist', content="""
            url_timeout=69d url_refresh=42d
            @foo https://foob.ar/
        """):
            iplists = parse_config_iplist(minimal_config())
            options = iplists['@foo'].options
            self.assertEqual(options.url_timeout, parse_duration('69d', 0))
            self.assertEqual(options.url_refresh, parse_duration('42d', 0))

    @unittest.mock.patch('foomuuri.fail', side_effect=SystemExit)
    def test_first_invalid_default_option(self, fail, *_):
        """Test first invalid default option on single line."""
        with self.mock_config_foomuuri(section='iplist', content="""
            invalid url_timeout=2d url_refresh=1d
            @foo https://foob.ar/
        """) as config_file:
            with self.assertRaises(SystemExit):
                _ = parse_config_iplist(minimal_config())

            fail.assert_called_once_with(
                f'File {config_file} line 4: Invalid iplist name: '
                'invalid url_timeout=2d url_refresh=1d'
            )

    @unittest.mock.patch('foomuuri.fail', side_effect=SystemExit)
    def test_second_invalid_default_option(self, fail, *_):
        """Test second invalid default option on single line."""
        with self.mock_config_foomuuri(section='iplist', content="""
            url_timeout=2d invalid url_refresh=1d
            @foo https://foob.ar/
        """) as config_file:
            with self.assertRaises(SystemExit):
                _ = parse_config_iplist(minimal_config())

            fail.assert_called_once_with(
                f'File {config_file} line 4: Unsupported syntax: '
                'url_timeout=2d invalid url_refresh=1d'
            )

    @unittest.mock.patch('foomuuri.fail', side_effect=SystemExit)
    def test_invalid_default_option_name(self, fail, *_):
        """Test invalid default option name."""
        with self.mock_config_foomuuri(section='iplist', content="""
            invalid_option=whatever_value
        """) as config_file:
            with self.assertRaises(SystemExit):
                _ = parse_config_iplist(minimal_config())

            fail.assert_called_once_with(
                f'File {config_file} line 4: Invalid iplist{{}} option name: '
                'invalid_option=whatever_value'
            )

    @unittest.mock.patch('foomuuri.fail', side_effect=SystemExit)
    def test_invalid_default_option_value(self, fail, *_):
        """Test invalid default option value."""
        with self.mock_config_foomuuri(section='iplist', content="""
            url_max_size=abcd
        """) as config_file:
            with self.assertRaises(SystemExit):
                _ = parse_config_iplist(minimal_config())

            fail.assert_called_once_with(
                f'File {config_file} line 4: Invalid iplist{{}} option value: '
                'url_max_size=abcd'
            )

    def test_start_merge_url_size_options(self, *_):
        """Test start, merge, url_size options."""
        with self.mock_config_foomuuri(section='iplist', content="""
            -start -merge url_max_size=1024
            @foo https://foob.ar/
            @bar https://b.ar/ start=no merge=no
            @baz https://b.az/ start=yes merge=yes url_max_size=2048
        """):
            iplists = parse_config_iplist(minimal_config())
            default_options = IPListOptions()
            # Testing applcation as default options
            # Asserting applied options differ from default values
            self.assertNotEqual(
                iplists['@foo'].options.start, default_options.start
            )
            self.assertNotEqual(
                iplists['@foo'].options.merge, default_options.merge
            )
            self.assertNotEqual(
                iplists['@foo'].options.url_max_size,
                default_options.url_max_size
            )
            # Asserting applied option values are exactly as set
            self.assertFalse(iplists['@foo'].options.start)
            self.assertFalse(iplists['@foo'].options.merge)
            self.assertEqual(iplists['@foo'].options.url_max_size, 1024)
            # Alternative start/merge syntax (false)
            self.assertFalse(iplists['@bar'].options.start)
            self.assertFalse(iplists['@bar'].options.merge)
            # Alternative start/merge syntax (true)
            self.assertTrue(iplists['@baz'].options.start)
            self.assertTrue(iplists['@baz'].options.merge)
            # Iplist url_max_size overrides default option
            self.assertTrue(iplists['@baz'].options.url_max_size, 2048)

    @unittest.mock.patch('foomuuri.warning')
    def test_iplist_sources_overwrite(self, warning, *_):
        """Test overwriting of iplist sources."""
        with self.mock_config_foomuuri(section='iplist', content="""
            @foo https://foob.ar/
            @foo https://rabo.of/
        """) as config_file:
            iplists = parse_config_iplist(minimal_config())
            self.assertEqual(
                iplists['@foo'].sources,
                ['https://rabo.of/'],
            )
            warning.assert_called_with(
                f'File {config_file} line 5: Overwriting iplist "@foo" '
                'with value "https://rabo.of/"'
            )

    def test_iplist_sources_append(self, *_):
        """Test appending of iplist sources."""
        with self.mock_config_foomuuri(section='iplist', content="""
            @foo https://foob.ar/
            @foo + https://rabo.of/

            @bar + https://foo.bar/

            @baz +
        """):
            iplists = parse_config_iplist(minimal_config())
            self.assertEqual(
                iplists['@foo'].sources,
                ['https://foob.ar/', 'https://rabo.of/'],
            )
            self.assertEqual(iplists['@bar'].sources, ['https://foo.bar/'])
            self.assertEqual(iplists['@baz'].sources, [])

    def test_intermixing_iplist_sources_options(self, *_):
        """Test itermixing of iplist sources and options."""
        with self.mock_config_foomuuri(section='iplist', content="""
            @foo start=no https://foob.ar/ merge=no https://rabo.of/
        """):
            iplists = parse_config_iplist(minimal_config())
            default_options = IPListOptions()
            # Asserting applied options differ from default values
            self.assertNotEqual(
                iplists['@foo'].options.start, default_options.start
            )
            self.assertNotEqual(
                iplists['@foo'].options.merge, default_options.merge
            )
            # Asserting appled options values are exactly as set
            self.assertFalse(iplists['@foo'].options.start)
            self.assertFalse(iplists['@foo'].options.merge)
            self.assertEqual(
                iplists['@foo'].sources,
                ['https://foob.ar/', 'https://rabo.of/'],
            )

    def test_last_option_priority_wins(self, *_):
        """Test last option defined for same ipset definition wins."""
        with self.mock_config_foomuuri(section='iplist', content="""
            @foo url_timeout=42d
            @foo url_timeout=69d
        """):
            iplists = parse_config_iplist(minimal_config())
            self.assertEqual(
                iplists['@foo'].options.url_timeout, parse_duration('69d', 0)
            )

    @unittest.mock.patch('foomuuri.verbose')
    def test_iplist_name_and_sources_vebose_output(self, verbose,
                                                   CONFIG, *_):
        """Test output of iplists name and sources when verbose >= 2."""
        with self.mock_config_foomuuri(section='iplist', content="""
            @foo https://foob.ar/
            @bar https://foo.bar/
        """):
            CONFIG.verbose = 2
            _ = parse_config_iplist(minimal_config())
            verbose.assert_has_calls([
                unittest.mock.call('@foo       https://foob.ar/'),
                unittest.mock.call('@bar       https://foo.bar/'),
            ])

    def test_internal_iplist_missing_ok_init(self, _, INTERNAL, *__):
        """Test INTERNAL.iplist_missing_ok is initialized."""
        with self.mock_config_foomuuri():
            self.assertRaises(
                AttributeError, lambda: INTERNAL.iplist_missing_ok
            )
            _ = parse_config_iplist(minimal_config())
            self.assertEqual(INTERNAL.iplist_missing_ok, set())
