"""Basic unit tests of read_config()."""
# pylint: disable=invalid-name,import-error

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
        """) as config_file:
            config = read_config(require_etc_config=False)
            self.assertDictEqual(
                config,
                {
                    '_section_line': {
                        'iplist': f'File {config_file} line 2: '
                    },
                    'iplist': [],
                },
            )

    def test_non_empty_section(self):
        """Test section with content."""
        with self.mock_config("""
            iplist {
                url_timeout 1d
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

    def test_section_line_continuation(self):
        """Test line continuation within section."""
        with self.mock_config("""
            iplist {
                url_timeout \\
                1d
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
        \\""") as config_file,
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

    def test_section_with_arguments(self):
        """Test section with arguments."""
        with self.mock_config("""
            prerouting filter mangle - 10 {
            }
        """) as config_file:
            config = read_config(require_etc_config=False)
            self.assertDictEqual(
                config,
                {
                    '_section_line': {
                        'prerouting filter mangle - 10': f'File {config_file} '
                        'line 2: '
                    },
                    'prerouting filter mangle - 10': [],
                },
            )

    def test_argument_for_argumentless_section(self):
        """Test passing argument to section not supposed to have one."""
        with (
            self.mock_config("""
            iplist argument {
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
                'take parameters: iplist argument {'
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
        """) as config_file:
            config = read_config(require_etc_config=False)
            self.assertDictEqual(
                config,
                {
                    '_section_line': {
                        'iplist': f'File {config_file} line 3: '
                    },
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
