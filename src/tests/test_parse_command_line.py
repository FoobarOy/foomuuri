"""Basic unit tests of parse_command_line()."""
# pylint: disable=invalid-name,import-error
# ruff: noqa: N803

import copy
import unittest
import unittest.mock

from foomuuri import CONFIG as BASE_CONFIG
from foomuuri import INTERNAL as BASE_INTERNAL
from foomuuri import parse_command_line


@unittest.mock.patch('foomuuri.CONFIG_OVERRIDE', new_callable=dict)
@unittest.mock.patch(
    'foomuuri.CONFIG', new_callable=lambda: copy.deepcopy(BASE_CONFIG)
)
@unittest.mock.patch(
    'foomuuri.INTERNAL', new_callable=lambda: copy.deepcopy(BASE_INTERNAL)
)
class TestParseCommandLine(unittest.TestCase):
    """Test parse_command_line()."""

    @unittest.mock.patch('sys.argv', ['foomuuri'])
    def test_no_arguments(self, INTERNAL, *_):
        """Test no arguments."""
        parse_command_line()
        self.assertEqual(INTERNAL.command, '')
        self.assertEqual(INTERNAL.parameters, [])

    @unittest.mock.patch('sys.argv', ['foomuuri', '--help'])
    def test_option_help(self, INTERNAL, *_):
        """Test --help option (sets 'help' command)."""
        parse_command_line()
        self.assertEqual(INTERNAL.command, 'help')
        self.assertEqual(INTERNAL.parameters, [])

    @unittest.mock.patch('sys.argv', ['foomuuri', '--version'])
    def test_option_version(self, INTERNAL, *_):
        """Test --version option (sets 'version' command)."""
        parse_command_line()
        self.assertEqual(INTERNAL.command, 'version')
        self.assertEqual(INTERNAL.parameters, [])

    @unittest.mock.patch(
        'sys.argv',
        ['foomuuri', '--verbose', 'command', 'arg1', '--force', 'arg2'],
    )
    def test_command_and_options(self, INTERNAL, CONFIG, CONFIG_OVERRIDE):
        """Test command with arguments, mixed with options."""
        parse_command_line()
        self.assertEqual(INTERNAL.command, 'command')
        self.assertEqual(INTERNAL.parameters, ['arg1', 'arg2'])
        self.assertEqual(INTERNAL.force, 1)
        self.assertEqual(CONFIG.verbose, 1)
        self.assertEqual(CONFIG_OVERRIDE['verbose'], 1)

    @unittest.mock.patch('sys.argv', ['foomuuri', '--syslog', '--fork'])
    def test_options_syslog_fork(self, INTERNAL, CONFIG, CONFIG_OVERRIDE):
        """Test --syslog and --fork options."""
        parse_command_line()
        self.assertEqual(CONFIG.syslog, 1)
        self.assertEqual(CONFIG.fork, 1)
        self.assertEqual(CONFIG_OVERRIDE['syslog'], 1)
        self.assertEqual(CONFIG_OVERRIDE['fork'], 1)
        self.assertEqual(INTERNAL.command, '')
        self.assertEqual(INTERNAL.parameters, [])

    @unittest.mock.patch('sys.argv', ['foomuuri', '--verbose'])
    def test_option_verbose(self, INTERNAL, CONFIG, CONFIG_OVERRIDE):
        """Test --verbose option."""
        parse_command_line()
        self.assertEqual(CONFIG.verbose, 1)
        self.assertEqual(CONFIG_OVERRIDE['verbose'], 1)
        self.assertEqual(INTERNAL.command, '')
        self.assertEqual(INTERNAL.parameters, [])

    @unittest.mock.patch('sys.argv', ['foomuuri', '--verbose', '--verbose'])
    def test_options_verbose_verbose(self, INTERNAL, CONFIG, CONFIG_OVERRIDE):
        """Test --verbose --verbose options."""
        parse_command_line()
        self.assertEqual(CONFIG.verbose, 2)
        self.assertEqual(CONFIG_OVERRIDE['verbose'], 2)
        self.assertEqual(INTERNAL.command, '')
        self.assertEqual(INTERNAL.parameters, [])

    @unittest.mock.patch('sys.argv', ['foomuuri', '--quiet'])
    def test_option_quiet(self, INTERNAL, CONFIG, CONFIG_OVERRIDE):
        """Test --quiet option."""
        parse_command_line()
        self.assertEqual(CONFIG.verbose, -1)
        self.assertEqual(CONFIG_OVERRIDE['verbose'], -1)
        self.assertEqual(INTERNAL.command, '')
        self.assertEqual(INTERNAL.parameters, [])

    @unittest.mock.patch('sys.argv', ['foomuuri', '--verbose', '--quiet'])
    def test_options_verbose_quiet(self, INTERNAL, CONFIG, CONFIG_OVERRIDE):
        """Test --verbose --quiet options."""
        parse_command_line()
        self.assertEqual(CONFIG.verbose, 0)
        self.assertEqual(CONFIG_OVERRIDE['verbose'], 0)
        self.assertEqual(INTERNAL.command, '')
        self.assertEqual(INTERNAL.parameters, [])

    @unittest.mock.patch('sys.argv', ['foomuuri', '--force'])
    def test_option_force(self, INTERNAL, *_):
        """Test --force option."""
        parse_command_line()
        self.assertEqual(INTERNAL.force, 1)
        self.assertEqual(INTERNAL.command, '')
        self.assertEqual(INTERNAL.parameters, [])

    @unittest.mock.patch('sys.argv', ['foomuuri', '--soft'])
    def test_option_soft(self, INTERNAL, *_):
        """Test --soft option."""
        parse_command_line()
        self.assertEqual(INTERNAL.force, -1)
        self.assertEqual(INTERNAL.command, '')
        self.assertEqual(INTERNAL.parameters, [])

    @unittest.mock.patch('sys.argv', ['foomuuri', '--set'])
    @unittest.mock.patch('foomuuri.fail', side_effect=SystemExit)
    def test_option_set_unknown(self, fail, *_):
        """Test --set option without suffix."""
        self.assertRaises(SystemExit, parse_command_line)
        fail.assert_called_with('Unknown option: --set')

    @unittest.mock.patch('sys.argv', ['foomuuri', '--set='])
    @unittest.mock.patch('foomuuri.fail', side_effect=SystemExit)
    def test_option_set_invalid_syntax(self, fail, *_):
        """Test incomplete --set option syntax."""
        self.assertRaises(SystemExit, parse_command_line)
        fail.assert_called_with(
            'Invalid syntax for --set=OPTION=VALUE: --set='
        )

    @unittest.mock.patch('sys.argv', ['foomuuri', '--set=unknown=value'])
    @unittest.mock.patch('foomuuri.fail', side_effect=SystemExit)
    def test_option_set_unknown_option(self, fail, *_):
        """Test --set option with unknown foomuuri{} CONFIG option."""
        self.assertRaises(SystemExit, parse_command_line)
        fail.assert_called_with(
            'Unknown foomuuri{} option: unknown'
        )

    @unittest.mock.patch('sys.argv', ['foomuuri', '--set=priority_offset=yes'])
    @unittest.mock.patch('foomuuri.fail', side_effect=SystemExit)
    def test_option_set_invalid_value(self, fail, *_):
        """Test --set option with invalid value."""
        self.assertRaises(SystemExit, parse_command_line)
        fail.assert_called_with(
            'Invalid foomuuri{} option priority_offset value: yes'
        )

    @unittest.mock.patch(
        'sys.argv',
        ['foomuuri', '--set=priority_offset=42', '--set=set_size=1'],
    )
    def test_options_set_valid(self, INTERNAL, CONFIG, _):
        """Test --set options with valid foomuuri{} CONFIG option/value."""
        parse_command_line()
        self.assertEqual(CONFIG.priority_offset, 42)
        self.assertEqual(CONFIG.set_size, 1)
        self.assertEqual(INTERNAL.command, '')
        self.assertEqual(INTERNAL.parameters, [])

    @unittest.mock.patch('sys.argv', ['foomuuri', '--unknown'])
    @unittest.mock.patch('foomuuri.fail', side_effect=SystemExit)
    def test_unknown_option(self, fail, *_):
        """Test unknown option."""
        self.assertRaises(SystemExit, parse_command_line)
        fail.assert_called_with('Unknown option: --unknown')

    @unittest.mock.patch('sys.argv', ['foomuuri', 'command', '-h', '-v'])
    def test_option_short(self, INTERNAL, *_):
        """Test short options. They are parsed as parameters."""
        parse_command_line()
        self.assertEqual(INTERNAL.command, 'command')
        self.assertEqual(INTERNAL.parameters, ['-h', '-v'])

    @unittest.mock.patch('sys.argv', ['foomuuri', 'command', 'a', '-', 'b'])
    def test_option_hyphen(self, INTERNAL, *_):
        """Test hyphen. It is parsed as parameter."""
        parse_command_line()
        self.assertEqual(INTERNAL.command, 'command')
        self.assertEqual(INTERNAL.parameters, ['a', '-', 'b'])
