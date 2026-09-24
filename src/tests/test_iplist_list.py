"""Test iplist list filtering."""
# pylint: disable=import-error,invalid-name
# ruff: file-ignore[invalid-argument-name]

import copy
import unittest
from unittest import mock

import foomuuri
from foomuuri import INTERNAL as BASE_INTERNAL


@mock.patch(
    'foomuuri.INTERNAL', new_callable=lambda: copy.deepcopy(BASE_INTERNAL)
)
class TestIPListElementContains(unittest.TestCase):
    """Test iplist list filtering by IP address."""

    def test_address_network_match(self, *_):
        """Test address, containing network and host bits."""
        self.assertTrue(
            foomuuri.iplist_element_contains(
                '10.0.0.0/24', foomuuri.ipaddress.ip_network('10.0.0.1')
            )
        )
        self.assertTrue(
            foomuuri.iplist_element_contains(
                '10.0.0.0/24',
                foomuuri.ipaddress.ip_network('10.0.0.99/24', strict=False),
            )
        )
        self.assertFalse(
            foomuuri.iplist_element_contains(
                '10.0.0.1/32', foomuuri.ipaddress.ip_network('10.0.0.0/31')
            )
        )

    def test_range(self, *_):
        """Test range (interval) elements."""
        self.assertTrue(
            foomuuri.iplist_element_contains(
                '10.0.0.10-10.0.0.20',
                foomuuri.ipaddress.ip_network('10.0.0.15'),
            )
        )
        self.assertFalse(
            foomuuri.iplist_element_contains(
                '10.0.0.10-10.0.0.20',
                foomuuri.ipaddress.ip_network('10.0.0.20/31'),
            )
        )

    def test_ip_versions_mismatch(self, *_):
        """Test IPv4/IPv6 mismatch."""
        self.assertFalse(
            foomuuri.iplist_element_contains(
                '10.0.0.0/24', foomuuri.ipaddress.ip_network('2001:db8::1')
            )
        )


@mock.patch(
    'foomuuri.INTERNAL', new_callable=lambda: copy.deepcopy(BASE_INTERNAL)
)
class TestCommandIPListList(unittest.TestCase):
    """Test command_iplist_list() filtering and rc."""

    @staticmethod
    def run_command(INTERNAL, parameters, elements):
        """Run command with mocked configuration and nft output."""
        INTERNAL.parameters = parameters
        data = {'nftables': [{'set': {'elem': elements}}]}
        with (
            mock.patch('foomuuri.minimal_config', return_value={}),
            mock.patch(
                'foomuuri.parse_config_iplist', return_value={'@foo': {}}
            ),
            mock.patch('foomuuri.nft_json', side_effect=[data, {}]),
            mock.patch('foomuuri.print_table'),
        ):
            return foomuuri.command_iplist_list()

    def test_matching_needle_returns_success(self, INTERNAL):
        """Return 0 when needle matches an element."""
        self.assertEqual(
            self.run_command(
                INTERNAL,
                ['list', '@foo', '10.0.0.99/24'],
                ['10.0.0.0/24'],
            ),
            0,
        )

    def test_nonmatching_needle_returns_error(self, INTERNAL):
        """Return 1 when no element contains any needle."""
        self.assertEqual(
            self.run_command(
                INTERNAL, ['list', '@foo', '192.0.2.1'], ['10.0.0.0/24']
            ),
            1,
        )

    def test_no_needle_returns_success(self, INTERNAL):
        """Return zero for ordinary unfiltered listing."""
        self.assertEqual(
            self.run_command(INTERNAL, ['list', '@foo'], ['10.0.0.1']), 0
        )

    def test_unsupported_filter_fails(self, INTERNAL):
        """Test unsupported IP filtering fails with exact error message."""
        filters = (
            '10.0.0.1-10.0.0.2',
            '-10.0.0.1',
            '[2001:db8::1]',
        )
        for value in filters:
            with self.subTest(value=value):
                with (
                    mock.patch(
                        'foomuuri.fail', side_effect=SystemExit
                    ) as fail,
                    self.assertRaises(SystemExit),
                ):
                    self.run_command(INTERNAL, ['list', '@foo', value], [])
                fail.assert_called_once_with(
                    'Filtering by IP range, negative or bracketed value '
                    f'is not supported: {value}'
                )
