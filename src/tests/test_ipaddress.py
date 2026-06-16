"""Basic unit tests for test_ipv*_address() functions."""
# pylint: disable=import-error

import unittest

from foomuuri import get_ip_family


class TestIsIpAddress(unittest.TestCase):
    """Basic unit tests for get_ip_family()."""

    def test_ipv4_address(self):
        """Test for IPv4 address."""
        self.assertEqual(get_ip_family(''), 0)
        self.assertEqual(get_ip_family('[127.0.0.1]'), 0)

        self.assertEqual(get_ip_family('127.0.0.1'), 4)

    def test_ipv4_network(self):
        """Test for IPv4 network."""
        self.assertEqual(get_ip_family(''), 0)
        self.assertEqual(get_ip_family('127.0.0.0/-16'), 0)

        self.assertEqual(get_ip_family('127.0.0.0/8'), 4)

    def test_ipv4_range(self):
        """Test for IPv4 range."""
        self.assertEqual(get_ip_family('-'), 0)
        self.assertEqual(get_ip_family('127.0.0.0/8-127.0.0.0/8'), 0)
        self.assertEqual(get_ip_family('127.0.0.2-127.0.0.1'), 0)

        self.assertEqual(get_ip_family('127.0.0.1-127.0.0.1'), 4)
        self.assertEqual(get_ip_family('127.0.0.1-127.0.0.2'), 4)

    def test_ipv6_address(self):
        """Test for IPv6 address."""
        self.assertEqual(get_ip_family(''), 0)

        self.assertEqual(get_ip_family('::'), 6)
        self.assertEqual(get_ip_family('[::]'), 6)

    def test_ipv6_network(self):
        """Test for IPv6 network."""
        self.assertEqual(get_ip_family(''), 0)
        self.assertEqual(get_ip_family('::/129'), 0)
        self.assertEqual(get_ip_family('[::]/-64'), 0)

        self.assertEqual(get_ip_family('::/64'), 6)
        self.assertEqual(get_ip_family('::/-64'), 6)
        self.assertEqual(get_ip_family('[::]/64'), 6)

    def test_ipv6_range(self):
        """Test for IPv6 range."""
        self.assertEqual(get_ip_family('-'), 0)
        self.assertEqual(get_ip_family('1::/64-1::/64'), 0)
        self.assertEqual(get_ip_family('::-::/-64'), 0)
        self.assertEqual(get_ip_family('::2-::1'), 0)

        self.assertEqual(get_ip_family('::-::'), 6)
        self.assertEqual(get_ip_family('::1-::2'), 6)

    def test_allow_negative(self):
        """Test address detection for allow_negative=True/False."""
        self.assertEqual(get_ip_family('-127.0.0.1', allow_negative=True), 4)
        self.assertEqual(get_ip_family('-::', allow_negative=True), 6)
        self.assertEqual(get_ip_family('-127.0.0.1', allow_negative=False), 0)
        self.assertEqual(get_ip_family('-::', allow_negative=False), 0)
