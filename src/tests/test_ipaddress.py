"""Basic unit tests for test_ipv*_address() functions."""
# pylint: disable=import-error

import unittest

from foomuuri import is_ip_address, is_ipv4_address, is_ipv6_address


class TestIsIPv4Address(unittest.TestCase):
    """Basic unit tests for test_ipv4_address()."""
    def test_ipv4_address(self):
        """Test for IPv4 address."""
        self.assertFalse(is_ipv4_address('', allow_network=False))
        self.assertFalse(is_ipv4_address('::', allow_network=False))
        self.assertFalse(is_ipv4_address('127.0.0.0/8', allow_network=False))
        self.assertTrue(is_ipv4_address('127.0.0.1', allow_network=False))

    def test_ipv4_network(self):
        """Test for IPv4 network."""
        self.assertFalse(is_ipv4_address('', allow_network=True))
        self.assertFalse(is_ipv4_address('::/64', allow_network=True))
        self.assertTrue(is_ipv4_address('127.0.0.0/8', allow_network=True))
        self.assertTrue(is_ipv4_address('127.0.0.1/8', allow_network=True))

    def test_ipv4_range(self):
        """Test for IPv4 range."""
        self.assertFalse(is_ipv4_address('-'))
        self.assertFalse(is_ipv4_address('::-::'))
        self.assertFalse(is_ipv4_address('127.0.0.0/8-127.0.0.0/8'))
        self.assertFalse(is_ipv4_address('127.0.0.2-127.0.0.1'))
        self.assertTrue(is_ipv4_address('127.0.0.1-127.0.0.1'))
        self.assertTrue(is_ipv4_address('127.0.0.1-127.0.0.2'))


class TestIsIPv6Address(unittest.TestCase):
    """Basic unit tests for test_ipv6_address()."""
    def test_ipv6_address(self):
        """Test for IPv6 address."""
        self.assertFalse(is_ipv6_address('', allow_network=False))
        self.assertFalse(is_ipv6_address('127.0.0.1', allow_network=False))
        self.assertFalse(is_ipv6_address('[::]/64', allow_network=False))
        self.assertTrue(is_ipv6_address('::', allow_network=False))
        self.assertTrue(is_ipv6_address('[::]', allow_network=False))

    def test_ipv6_network(self):
        """Test for IPv6 network."""
        self.assertFalse(is_ipv6_address('', allow_network=True))
        self.assertFalse(is_ipv6_address('127.0.0.0/8', allow_network=True))
        self.assertFalse(is_ipv6_address('::/129', allow_network=True))
        self.assertFalse(is_ipv6_address('[::]/-64', allow_network=True))
        self.assertTrue(is_ipv6_address('::/64', allow_network=True))
        self.assertTrue(is_ipv6_address('::/-64', allow_network=True))
        self.assertTrue(is_ipv6_address('[::]/64', allow_network=True))

    def test_ipv6_range(self):
        """Test for IPv6 range."""
        self.assertFalse(is_ipv6_address('-'))
        self.assertFalse(is_ipv6_address('127.0.0.1-127.0.0.2'))
        self.assertFalse(is_ipv6_address('1::/64-1::/64'))
        self.assertFalse(is_ipv6_address('::-::/-64'))
        self.assertFalse(is_ipv6_address('::2-::1'))
        self.assertTrue(is_ipv6_address('::-::'))
        self.assertTrue(is_ipv6_address('::1-::2'))


class TestIsIPAddress(unittest.TestCase):
    """Basic unit tests for test_ip_address()."""
    def test_ip_address(self):
        """Test address detection for allow_negative=True/False."""
        self.assertEqual(is_ip_address('-127.0.0.1', allow_negative=True), 4)
        self.assertEqual(is_ip_address('-::', allow_negative=True), 6)
        self.assertEqual(is_ip_address('-127.0.0.1', allow_negative=False), 0)
        self.assertEqual(is_ip_address('-::', allow_negative=False), 0)
