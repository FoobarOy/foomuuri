"""Basic unit tests of TypedConfig."""
# pylint: disable=import-error

import pathlib
import unittest
from dataclasses import dataclass, field

from foomuuri import TypedConfig


class TestTypedConfig(unittest.TestCase):
    """Setters / getters / type conversion tests."""
    def set(self, name, value):
        """Set attribute and return value helper."""
        self.config[name] = value
        return self.config[name]

    def set_from_str(self, name, value):
        """Set attribute from string and return value helper."""
        self.config.set_from_str(name, value)
        return self.config[name]

    def append_from_str(self, name, value):
        """Append attribute value from string and return value helper."""
        self.config.append_from_str(name, value)
        return self.config[name]

    def setUp(self):
        @dataclass
        class TestConfig(TypedConfig):
            """Test class."""
            initialized_str: str = 'init_value1'
            uninitialized_str: str = field(init=False)
            initialized_untyped = 'init_value2'
            type_conversion_int: int = 0
            type_conversion_list: list = field(default_factory=list)
            type_conversion_posixpath: pathlib.PosixPath = field(init=False)
            validation: str = field(
                init=False, metadata={'validate': lambda v: v != ''}
            )
            conversion: list = field(
                init=False, metadata={'convert_str': lambda v: v.split()}
            )

        self.config = TestConfig()

    def test_accessor_style(self):
        """Test dict/dot style accessor/setter."""
        self.config.initialized_str = 'new_value1'
        self.assertEqual(self.config.initialized_str, 'new_value1')
        self.assertRaises(
            AttributeError, lambda: self.config.unknown_attribute
        )

        self.config['initialized_str'] = 'new_value2'
        self.assertEqual(self.config['initialized_str'], 'new_value2')
        self.assertRaises(
            AttributeError, lambda: self.config['unknown_attribute']
        )

        self.assertRaises(
            AttributeError, self.set, 'unknown_attribute', '123'
        )

    def test_initialized_typed(self):
        """Test assigning values to initialized typed attributes."""
        self.assertRaises(TypeError, self.set, 'initialized_str', 123)
        self.assertEqual(self.set('initialized_str', 'value'), 'value')

    def test_uninitialized_typed(self):
        """Test assigning values to uninialized typed attributes."""
        self.assertRaises(
            AttributeError, lambda: self.config.uninitialized_str
        )
        self.assertRaises(TypeError, self.set, 'uninitialized_str', 123)
        self.assertEqual(self.set('uninitialized_str', 'value'), 'value')

    def test_initialized_untyped(self):
        """Test accessing listed untyped attributes."""
        self.assertRaises(
            AttributeError, lambda: self.config.uninitialized_untyped
        )

    def test_set_from_str(self):
        """Test attribute type conversion from str (set_from_str)."""
        # Invalid value type: only str supported
        self.assertRaises(
            TypeError, self.config.set_from_str, 'type_conversion_int', 123
        )
        # Supported conversion, from str to int
        self.assertEqual(
            self.set_from_str('type_conversion_int', '123'), 123
        )
        # Supported conversion, from str to pathlib.PosixPath
        self.assertEqual(
            self.set_from_str('type_conversion_posixpath', '/tmp/'),
            pathlib.PosixPath('/tmp/')
        )
        # Assignment, str to str
        self.assertEqual(self.set_from_str('initialized_str', '123'), '123')
        # Assignment, list converted from str
        self.assertEqual(self.set_from_str('conversion', '1'), ['1'])
        # Unsupported conversion, from str to list
        self.assertRaises(
            TypeError, self.config.set_from_str, 'type_conversion_list', '[]'
        )
        # Assign non-existing attribute
        self.assertRaises(
            AttributeError, self.config.set_from_str, 'unknownattribute', '123'
        )

    def test_append_from_str(self):
        """Test attribute value append from str (append_from_str)."""
        # Invalid value type: only str supported
        self.assertRaises(
            TypeError, self.config.append_from_str, 'initialized_str', 123
        )
        # Appending, str to str
        self.assertEqual(self.set_from_str('initialized_str', '1'), '1')
        self.assertEqual(self.append_from_str('initialized_str', '2'), '1 2')
        # Appending, list converted from str to list
        self.assertEqual(self.set_from_str('conversion', '1'), ['1'])
        self.assertEqual(self.append_from_str('conversion', '2'), ['1', '2'])
        # Unsupported append, from str to int
        self.assertRaises(
            TypeError, self.append_from_str, 'type_conversion_int', '1'
        )
        # Append non-existing attribute
        self.assertRaises(
            AttributeError, self.append_from_str, 'unknownattribute', '123'
        )

    def test_validation(self):
        """Test attribute validation helper call."""
        self.assertRaises(ValueError, self.set, 'validation', '')
        self.assertEqual(self.set('validation', 'test'), 'test')

    def test_iter(self):
        """Test __iter__."""
        self.assertEqual(sorted(self.config), [
            'conversion',
            'initialized_str',
            'type_conversion_int',
            'type_conversion_list',
            'type_conversion_posixpath',
            'uninitialized_str',
            'validation',
        ])

    def test_get(self):
        """Test get."""
        self.assertEqual(self.config.get('initialized_str'), 'init_value1')
        self.assertEqual(self.config.get('unknown_attr'), None)
