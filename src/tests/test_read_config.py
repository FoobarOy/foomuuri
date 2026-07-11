"""Basic unit tests of read_config()."""
# pylint: disable=invalid-name,import-error,too-many-public-methods
# ruff: noqa: PLR0904 (too-many-public-methods)

import contextlib
import unittest
import unittest.mock

from foomuuri import read_config


class TestReadConfig(unittest.TestCase):
    """Basic unit tests of read_config()."""

    @staticmethod
    @contextlib.contextmanager
    def mock_config(config_text: str):
        """Return context manager of foomuuri.find_config_files() patch.

        See test_config_foomuuri.py for detailed explanation.
        """
        config_file = unittest.mock.MagicMock()
        config_file.read_text.return_value = config_text
        with unittest.mock.patch(
            'foomuuri.find_config_files', side_effect=[[], [config_file]]
        ):
            yield config_file

    def test_empty_section(self):
        """Test section without content."""
        with self.mock_config("""
            iplist {
            }
            foomuuri { }
        """) as config_file:
            config = read_config(require_etc_config=False)
            self.assertDictEqual(
                config,
                {
                    '_section_line': {
                        'foomuuri': f'File {config_file} line 4: ',
                        'iplist': f'File {config_file} line 2: ',
                    },
                    'foomuuri': [],
                    'iplist': [],
                },
            )

    def test_non_empty_section(self):
        """Test section with content."""
        with self.mock_config("""
            iplist {
                url_timeout 1d
            }
            foomuuri { priority_offset 42 }
        """) as config_file:
            config = read_config(require_etc_config=False)
            self.assertDictEqual(
                config,
                {
                    '_section_line': {
                        'foomuuri': f'File {config_file} line 5: ',
                        'iplist': f'File {config_file} line 2: ',
                    },
                    'iplist': [
                        (f'File {config_file} line 3: ', ['url_timeout', '1d'])
                    ],
                    'foomuuri': [
                        (
                            f'File {config_file} line 5: ',
                            ['priority_offset', '42'],
                        )
                    ],
                },
            )

    def test_section_line_continuation(self):
        """Test line continuation within section."""
        with self.mock_config("""
            iplist {
                url_timeout \\
                1d
            }
            foomuuri { priority_offset \\
            42 }
        """) as config_file:
            config = read_config(require_etc_config=False)
            self.assertDictEqual(
                config,
                {
                    '_section_line': {
                        'foomuuri': f'File {config_file} line 7: ',
                        'iplist': f'File {config_file} line 2: ',
                    },
                    'foomuuri': [
                        (
                            f'File {config_file} line 7: ',
                            ['priority_offset', '42'],
                        )
                    ],
                    'iplist': [
                        (f'File {config_file} line 4: ', ['url_timeout', '1d'])
                    ],
                },
            )

    def test_last_line_continuation(self):
        """Test line continuation at config last line."""
        with (
            self.mock_config("""
            iplist {
            }
        \\""") as config_file,
            unittest.mock.patch(
                'foomuuri.fail', side_effect=SystemExit
            ) as fail,
        ):
            self.assertRaises(
                SystemExit, read_config, require_etc_config=False
            )
            fail.assert_called_once_with(
                f'File {config_file}: Continuation "\\" at end of file'
            )

    def test_content_outside_section(self):
        """Test content outside section."""
        with (
            self.mock_config("""
            iplist {
            }
            url_timeout 1d
        """) as config_file,
            unittest.mock.patch(
                'foomuuri.fail', side_effect=SystemExit
            ) as fail,
        ):
            self.assertRaises(
                SystemExit, read_config, require_etc_config=False
            )
            fail.assert_called_once_with(
                f'File {config_file} line 4: Unknown line: url_timeout 1d'
            )

    def test_content_outside_inline_section(self):
        """Test content outside inline section."""
        with (
            self.mock_config("""
            iplist { } url_timeout 1d
        """) as config_file,
            unittest.mock.patch(
                'foomuuri.fail', side_effect=SystemExit
            ) as fail,
        ):
            self.assertRaises(
                SystemExit, read_config, require_etc_config=False
            )
            fail.assert_called_once_with(
                f'File {config_file} line 2: '
                'Closing brace must be last: iplist { } url_timeout 1d'
            )

    def test_section_with_parameters(self):
        """Test section with parameters."""
        with self.mock_config("""
            prerouting filter mangle - 10 {
            }
            template template_name { }
        """) as config_file:
            config = read_config(require_etc_config=False)
            self.assertDictEqual(
                config,
                {
                    '_section_line': {
                        'prerouting filter mangle - 10': f'File {config_file} '
                        'line 2: ',
                        'template template_name': f'File {config_file} '
                        'line 4: ',
                    },
                    'prerouting filter mangle - 10': [],
                    'template template_name': [],
                },
            )

    def test_section_with_single_word_parameter(self):
        """Test section accepting single word parameter only."""
        with (
            self.mock_config("""
            template param1 param2 {
            }
        """) as config_file,
            unittest.mock.patch(
                'foomuuri.fail', side_effect=SystemExit
            ) as fail,
        ):
            self.assertRaises(
                SystemExit, read_config, require_etc_config=False
            )
            fail.assert_called_once_with(
                f'File {config_file} line 2: Section "template" '
                'must have single word name: template param1 param2 {'
            )

    def test_parameter_for_parameterless_section(self):
        """Test passing parameter to section not supposed to have one."""
        with (
            self.mock_config("""
            iplist parameter {
            }
        """) as config_file,
            unittest.mock.patch(
                'foomuuri.fail', side_effect=SystemExit
            ) as fail,
        ):
            self.assertRaises(
                SystemExit, read_config, require_etc_config=False
            )
            fail.assert_called_once_with(
                f'File {config_file} line 2: Section "iplist" does not '
                'take parameters: iplist parameter {'
            )

    def test_section_missing_closing_brace(self):
        """Test section without closing brace."""
        with (
            self.mock_config("""
            iplist {
                url_timeout 1d
        """) as config_file,
            unittest.mock.patch(
                'foomuuri.fail', side_effect=SystemExit
            ) as fail,
        ):
            self.assertRaises(
                SystemExit, read_config, require_etc_config=False
            )
            fail.assert_called_once_with(
                f'File {config_file}: Section "iplist" is missing '
                '"}" at end of file'
            )

    def test_inline_section_missing_closing_brace(self):
        """Test inline_section without closing brace."""
        with (
            self.mock_config("""
            iplist { url_timeout 1d
        """) as config_file,
            unittest.mock.patch(
                'foomuuri.fail', side_effect=SystemExit
            ) as fail,
        ):
            self.assertRaises(
                SystemExit, read_config, require_etc_config=False
            )
            fail.assert_called_once_with(
                f'File {config_file} line 2: '
                'Closing brace missing: iplist { url_timeout 1d'
            )

    def test_stray_closing_brace(self):
        """Test stray closing brace."""
        with (
            self.mock_config("""
            iplist {
            }
            }
        """) as config_file,
            unittest.mock.patch(
                'foomuuri.fail', side_effect=SystemExit
            ) as fail,
        ):
            self.assertRaises(
                SystemExit, read_config, require_etc_config=False
            )
            fail.assert_called_once_with(
                f'File {config_file} line 4: Extra "}}"'
            )

    def test_inline_section_extra_closing_brace(self):
        """Test inline section with extra closing brace."""
        with (
            self.mock_config("""
            foomuuri { bar } }
        """) as config_file,
            unittest.mock.patch(
                'foomuuri.fail', side_effect=SystemExit
            ) as fail,
        ):
            self.assertRaises(
                SystemExit, read_config, require_etc_config=False
            )
            fail.assert_called_once_with(
                f'File {config_file} line 2: '
                'One closing brace allowed: foomuuri { bar } }'
            )

    def test_inline_section_extra_opening_braces(self):
        """Test extra opening braces for inline section."""
        with (
            self.mock_config("""
            foomuuri { bar } iplist {
        """) as config_file,
            unittest.mock.patch(
                'foomuuri.fail', side_effect=SystemExit
            ) as fail,
        ):
            self.assertRaises(
                SystemExit, read_config, require_etc_config=False
            )
            fail.assert_called_once_with(
                f'File {config_file} line 2: '
                'One opening brace allowed: foomuuri { bar } iplist {'
            )

    def test_section_nesting(self):
        """Test section nesting."""
        with (
            self.mock_config("""
            iplist {
                template {
                }
            }
        """) as config_file,
            unittest.mock.patch(
                'foomuuri.fail', side_effect=SystemExit
            ) as fail,
        ):
            self.assertRaises(
                SystemExit, read_config, require_etc_config=False
            )
            fail.assert_called_once_with(
                f'File {config_file} line 3: New "template {{" '
                'while section "iplist" is still open'
            )

    def test_section_missing_opening_brace(self):
        """Test section without opening brace."""
        with (
            self.mock_config("""
            iplist
                url_timeout 1d
            }
        """) as config_file,
            unittest.mock.patch(
                'foomuuri.fail', side_effect=SystemExit
            ) as fail,
        ):
            self.assertRaises(
                SystemExit, read_config, require_etc_config=False
            )
            fail.assert_called_once_with(
                f'File {config_file} line 2: Unknown line: iplist'
            )

    def test_comments(self):
        """Test comments inside and outside section."""
        with self.mock_config("""
            # comment outside
            iplist {    # comment on section start
                # comment inside section
                url_timeout 1d      # comment section content
            }   # comment on section close

            foomuuri { priority_offset 42 }    # comment inline section
        """) as config_file:
            config = read_config(require_etc_config=False)
            self.assertDictEqual(
                config,
                {
                    '_section_line': {
                        'foomuuri': f'File {config_file} line 8: ',
                        'iplist': f'File {config_file} line 3: ',
                    },
                    'foomuuri': [
                        (
                            f'File {config_file} line 8: ',
                            ['priority_offset', '42'],
                        )
                    ],
                    'iplist': [
                        (f'File {config_file} line 5: ', ['url_timeout', '1d'])
                    ],
                },
            )

    def test_protected_section(self):
        """Test that section starting with _ is rejected."""
        with (
            self.mock_config("""
                _section {
                }
            """) as config_file,
            unittest.mock.patch(
                'foomuuri.fail', side_effect=SystemExit
            ) as fail,
        ):
            self.assertRaises(
                SystemExit, read_config, require_etc_config=False
            )
            fail.assert_called_once_with(
                f'File {config_file} line 2: Unknown section: _section'
            )

    def test_empty_config(self):
        """Test empty config file."""
        with self.mock_config(''):
            config = read_config(require_etc_config=False)
            self.assertDictEqual(
                config,
                {'_section_line': {}},
            )

    def test_config_reading_stop_word(self):
        """Test that config reading stops on '# foomuuri: not-conf' marker."""
        with self.mock_config("""
            iplist {
                url_timeout 1d
            }
# foomuuri: not-conf
            foomuuri {
                priority_offset 42
            }
        """) as config_file:
            config = read_config(require_etc_config=False)
            self.assertDictEqual(
                config,
                {
                    '_section_line': {
                        'iplist': f'File {config_file} line 2: '
                    },
                    'iplist': [
                        (f'File {config_file} line 3: ', ['url_timeout', '1d'])
                    ],
                },
            )
