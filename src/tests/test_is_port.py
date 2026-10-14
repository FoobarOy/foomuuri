"""Basic unit tests for is_port()."""
# pylint: disable=import-error

import unittest.mock

from foomuuri import Rule, is_port


class TestIsPort(unittest.TestCase):
    """Basic unit tests for is_port()."""

    def run_is_port(
        self,
        protocol: str,
        value: str,
        expected: bool,
        warn_output: bool = False,
    ) -> None:
        """Run single test."""
        with unittest.mock.patch('foomuuri.warning') as warning:
            rule = Rule(protocol=protocol, fileline='', line=[])
            ret = is_port(value, rule)
            self.assertEqual(ret, expected)
            if warn_output:
                warning.assert_called_once()
            else:
                warning.assert_not_called()

    def test_valid(self):
        """Test valid values."""
        for item in (
            'tcp 22',
            'tcp 1-3',
            'tcp -2',
            'icmp 8',
            'icmp redirect',
            'icmp echo-request',
        ):
            protocol, value = item.split(' ', 1)
            self.run_is_port(protocol, value, True)

    def test_invalid(self):
        """Test invalid values."""
        for item in (
            'tcp -',
            'tcp a',
            'tcp 1.1',
            'tcp 1-',
            'tcp -1-',
            'tcp foo',
            'tcp ,',
            'tcp 9,',
            'icmp foo',
        ):
            protocol, value = item.split(' ', 1)
            self.run_is_port(protocol, value, False)

    def test_warning(self):
        """Test accepted values with warning output."""
        for item in (
            'tcp 1,2',
            'tcp 1,2-3',
            'icmp redirect,8',
        ):
            protocol, value = item.split(' ', 1)
            self.run_is_port(protocol, value, True, True)
