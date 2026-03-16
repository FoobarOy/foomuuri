"""Basic unit tests of parse_command_line()."""
# pylint: disable=invalid-name,import-error
# ruff: noqa: N803

import contextlib
import copy
import unittest
import unittest.mock

from foomuuri import CONFIG as BASE_CONFIG
from foomuuri import INTERNAL as BASE_INTERNAL
from foomuuri import minimal_config


@unittest.mock.patch(
    'foomuuri.INTERNAL', new_callable=lambda: copy.deepcopy(BASE_INTERNAL)
)
@unittest.mock.patch(
    'foomuuri.CONFIG', new_callable=lambda: copy.deepcopy(BASE_CONFIG)
)
class TestParseConfigFoomuuri(unittest.TestCase):
    """Test parse_config_foomuuri()."""
    @staticmethod
    @contextlib.contextmanager
    def mock_config_foomuuri(option, value):
        """Return context manager of foomuuri.find_config_files() patch.

        foomuuri.find_config_files() is patched to return generated
        foomuuri configuration file, containing foomuuri{} section
        with single option/value."""
        # MagicMock of pathlib.PosixPAth returning desired foomuuri config
        config_file = unittest.mock.MagicMock(
          **{
             'read_text.return_value': f"""
              foomuuri {{
                  {option} {value}
              }}
          """
          })
        # foomuuri.find_config_files() is called by foomuuri.read_config()
        # to load configuration files.
        # read_config() tries loading share_config first, and etc_config then.
        # We only care about etc_config, therefore side_effect list passed
        # to foomuuri.find_config_files mock patch has two elemeents,
        # [] - empty share_config, and [config_file] - generated config.
        with unittest.mock.patch(
            'foomuuri.find_config_files', side_effect=[[], [config_file]]
        ):
            yield config_file

    def test_try_reload_timeout(self, CONFIG, *_):
        """Test try-reload_timeout backwards compatible option."""
        with self.mock_config_foomuuri('try-reload_timeout', 69):
            _ = minimal_config()
            self.assertEqual(CONFIG.try_reload_timeout, 69)

    def test_append_value(self, CONFIG, *_):
        """Test appending of option value."""
        with self.mock_config_foomuuri('log_level', '+ append'):
            _ = minimal_config()
            self.assertEqual(CONFIG.log_level, 'level info flags skuid append')

    def test_unknown_option(self, *_):
        """Test assigning unknown option."""
        with (
            self.mock_config_foomuuri(
                'unknown_option', 'value'
            ) as config_file,
            unittest.mock.patch(
                'foomuuri.fail', side_effect=SystemExit
            ) as fail,
        ):
            self.assertRaises(SystemExit, minimal_config)
            fail.assert_called_once_with(
                f'File {config_file} line 3: Unknown foomuuri{{}}'
                ' option: unknown_option value'
            )

    def test_invalid_value(self, *_):
        """Test assigning invalid value."""
        with (
            self.mock_config_foomuuri(
                'priority_offset', 'not_an_int'
            ) as config_file,
            unittest.mock.patch(
                'foomuuri.fail', side_effect=SystemExit
            ) as fail,
        ):
            self.assertRaises(SystemExit, minimal_config)
            fail.assert_called_once_with(
                f'File {config_file} line 3: Invalid foomuuri{{}}'
                ' option value: priority_offset not_an_int'
            )

    @unittest.mock.patch('foomuuri.CONFIG_OVERRIDE', new_callable=dict)
    def test_config_override(self, CONFIG_OVERRIDE, CONFIG, *_):
        """Test overriding of CONFIG from CONFIG_OVERRRIDE."""
        def test_override(option, override, config):
            with self.mock_config_foomuuri(option, '0'):
                CONFIG_OVERRIDE[option] = override
                _ = minimal_config()
                self.assertEqual(CONFIG[option], config)

        # Overriding with correct value type (str)
        test_override(option='priority_offset', override='69', config=69)
        # Overriding with invalid value type (int).
        test_override(option='priority_offset', override=69, config=69)

    def test_postprocess_priority_offset(self, _, INTERNAL):
        """Test postprocessing of priority_offset option."""
        def test_priority_offset(config, internal):
            with self.mock_config_foomuuri('priority_offset', config):
                _ = minimal_config()
                self.assertEqual(INTERNAL.priority_offset, internal)

        test_priority_offset(config=-1, internal=' - 1')
        test_priority_offset(config=0, internal='')
        test_priority_offset(config=1, internal=' + 1')

    def test_postprocess_log_rates(self, CONFIG, *_):
        """Test postprocessing of log_* rates options."""
        with self.mock_config_foomuuri('log_rate', '1/second burst 3'):
            _ = minimal_config()
            self.assertTrue(CONFIG.log_rate.endswith(' packets'))
