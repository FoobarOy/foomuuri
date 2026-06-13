"""Basic unit tests for test_ipv*_address() functions."""
# pylint: disable=import-error

import unittest

from foomuuri import is_ip_address


class TestIsIpAddress(unittest.TestCase):
    """Basic unit tests for is_ip_address()."""

    def test_ipv4_address(self):
        """Test for IPv4 address."""
        self.assertEqual(is_ip_address(''), 0)

        self.assertEqual(is_ip_address('[127.0.0.1]'), 0)
        self.assertEqual(is_ip_address('127.0.0.1'), 4)

    def test_ipv4_network(self):
        """Test for IPv4 network."""
        self.assertEqual(is_ip_address(''), 0)

        self.assertEqual(is_ip_address('127.0.0.0/8'), 4)

    def test_ipv4_range(self):
        """Test for IPv4 range."""
        self.assertEqual(is_ip_address('-'), 0)
        self.assertEqual(is_ip_address('127.0.0.0/8-127.0.0.0/8'), 0)
        self.assertEqual(is_ip_address('127.0.0.2-127.0.0.1'), 0)

        self.assertEqual(is_ip_address('127.0.0.1-127.0.0.1'), 4)
        self.assertEqual(is_ip_address('127.0.0.1-127.0.0.2'), 4)

    def test_ipv6_address(self):
        """Test for IPv6 address."""
        self.assertEqual(is_ip_address(''), 0)

        self.assertEqual(is_ip_address('::'), 6)
        self.assertEqual(is_ip_address('[::]'), 6)

    def test_ipv6_network(self):
        """Test for IPv6 network."""
        self.assertEqual(is_ip_address(''), 0)
        self.assertEqual(is_ip_address('::/129'), 0)
        self.assertEqual(is_ip_address('[::]/-64'), 0)

        self.assertEqual(is_ip_address('::/64'), 6)
        self.assertEqual(is_ip_address('::/-64'), 6)
        self.assertEqual(is_ip_address('[::]/64'), 6)

    def test_ipv6_range(self):
        """Test for IPv6 range."""
        self.assertEqual(is_ip_address('-'), 0)
        self.assertEqual(is_ip_address('1::/64-1::/64'), 0)
        self.assertEqual(is_ip_address('::-::/-64'), 0)
        self.assertEqual(is_ip_address('::2-::1'), 0)

        self.assertEqual(is_ip_address('::-::'), 6)
        self.assertEqual(is_ip_address('::1-::2'), 6)

    def test_allow_negative(self):
        """Test address detection for allow_negative=True/False."""
        self.assertEqual(is_ip_address('-127.0.0.1', allow_negative=True), 4)
        self.assertEqual(is_ip_address('-::', allow_negative=True), 6)
        self.assertEqual(is_ip_address('-127.0.0.1', allow_negative=False), 0)
        self.assertEqual(is_ip_address('-::', allow_negative=False), 0)
