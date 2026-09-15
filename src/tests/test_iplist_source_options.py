"""Unit tests of IPListSourceOptions.set_option()."""
# pylint: disable=invalid-name,import-error

import unittest.mock

from foomuuri import IPListSourceOptions


class TestIPListSourceOptionsSetOption(unittest.TestCase):
    """Test IPListSourceOptions set_option."""

    @staticmethod
    def run_set_option(name, new_value, source='https://foo.bar'):
        """Call IPListSourceOptions.set_option() with mocked warning."""
        options = IPListSourceOptions()
        with unittest.mock.patch('foomuuri.warning') as warning:
            options.set_option(name, new_value, source)
        return options, warning

    def test_set_over_default_none(self):
        """Test setting True or False over None."""
        for value in (True, False):
            with self.subTest(msg=''):
                options, warning = self.run_set_option('overwrite', value)
                self.assertEqual(options.overwrite, value)
                warning.assert_not_called()

    def test_set_none_over_none(self):
        """Test setting None over None."""
        options, warning = self.run_set_option('overwrite', None)
        self.assertIsNone(options.overwrite)
        warning.assert_not_called()

    def test_set_same_value(self):
        """Test setting True/False over the same value."""
        for value in (True, False):
            with self.subTest(msg=f'Setting {value} to {value}'):
                options = IPListSourceOptions()
                options.overwrite = value
                with unittest.mock.patch('foomuuri.warning') as warning:
                    options.set_option('overwrite', value, 'https://foo.bar')
                self.assertEqual(options.overwrite, value)
                warning.assert_not_called()

    def test_conflicting_value_warning(self):
        """Test flipping True<->False value emits warning."""
        options = IPListSourceOptions()
        options.overwrite = True

        for value in (True, False):
            with self.subTest(msg=f'Flipping {not value} to {value}'):
                options.overwrite = not value
                with unittest.mock.patch('foomuuri.warning') as warning:
                    options.set_option('overwrite', value, 'https://foo.bar')
                self.assertEqual(options.overwrite, value)
                warning.assert_called_once_with(
                    'Conflicting iplist source option "overwrite" for "https://foo.bar"'
                )

    def test_conflicting_none_keeps_value(self):
        """Test setting None over True/False prints warning and keeps value."""
        for value in (True, False):
            options = IPListSourceOptions()
            options.overwrite = value
            with unittest.mock.patch('foomuuri.warning') as warning:
                options.set_option('overwrite', None, 'https://foo.bar')
            self.assertEqual(options.overwrite, value)
            warning.assert_called_once_with(
                'Conflicting iplist source option "overwrite" for '
                '"https://foo.bar"'
            )
