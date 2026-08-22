"""Test parse_rule_line()."""
# pylint: disable=import-error

import unittest
import unittest.mock

from foomuuri import parse_rule_line


class TestParseRuleLine(unittest.TestCase):
    """Test parse_rule_line()."""

    @unittest.mock.patch('foomuuri.fail', side_effect=SystemExit)
    def test_incomplete_helper(self, fail):
        """Reject incomplete helper rule."""
        for line, error in (
            (['helper', 'ftp-21'], '"helper" without "protocol" is not valid'),
            (
                ['tcp', 'helper', 'ftp-21'],
                '"helper" without "dport" is not valid',
            ),
        ):
            with self.subTest(line=line):
                with self.assertRaises(SystemExit):
                    parse_rule_line(('File line: ', line))
                fail.assert_called_with(f'File line: {error}')

    def test_valid_helper(self):
        """Accept valid helper rule."""
        rule = parse_rule_line(
            ('File line: ', ['tcp', '21', 'helper', 'ftp-21'])
        )
        self.assertEqual(rule.protocol, 'tcp')
        self.assertEqual(rule.dport, '21')
        self.assertEqual(rule.helper, 'ftp-21')
