"""Basic unit tests of TypedConfig."""
# pylint: disable=import-error

import pathlib
import typing
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
        """Set up test data."""

        @dataclass
        class TestConfig(TypedConfig):
            """Test class."""

            # pylint: disable=too-many-instance-attributes
            initialized_str: str = 'init_value1'
            union_str_or_none: typing.Union[str, None] = None
            uninitialized_str: str = field(init=False)
            initialized_untyped = 'init_value2'  # ruff: ignore[implicit-class-var-in-dataclass]
            type_conversion_float: float = 0.0
            type_conversion_int: int = 0
            type_conversion_list: list = field(default_factory=list)
            type_conversion_posixpath: pathlib.PosixPath = field(init=False)
            type_conversion_set: set = field(default_factory=set)
            parametrized_list: list[str] = field(default_factory=list)
            parametrized_dict: dict[str, int] = field(default_factory=dict)
            parametrized_union: typing.Union[list[str], int] = field(
                default_factory=list
            )
            validation: str = field(
                init=False, metadata={'validate': lambda v: v}
            )
            conversion: list = field(
                init=False, metadata={'convert_str': lambda v: v.split()}
            )

        self.config = TestConfig()

    def test_accessor_style(self):
        """Test index and dot access and assignment."""
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

        self.assertRaises(AttributeError, self.set, 'unknown_attribute', '123')

    def test_parameterized_types(self):
        """Test assigning parametrized types attributes."""
        self.assertListEqual(
            self.set('parametrized_list', ['value']), ['value']
        )
        self.assertDictEqual(
            self.set('parametrized_dict', {'key': 1}), {'key': 1}
        )
        with self.assertRaises(TypeError):
            self.set('parametrized_list', {})
        with self.assertRaises(TypeError):
            self.set('parametrized_dict', [])

    def test_parameterized_union_types(self):
        """Test assigning to Union attributes with parametrized args."""
        self.assertEqual(self.set('parametrized_union', ['value']), ['value'])
        self.assertEqual(self.set('parametrized_union', 1), 1)
        with self.assertRaises(TypeError):
            self.set('parametrized_union', {'key': 1})

    def test_initialized_typed(self):
        """Test assignment to initialized typed attributes."""
        self.assertRaises(TypeError, self.set, 'initialized_str', 123)
        self.assertEqual(self.set('initialized_str', 'value'), 'value')

    def test_uninitialized_typed(self):
        """Test assignment to uninitialized typed attributes."""
        self.assertRaises(
            AttributeError, lambda: self.config.uninitialized_str
        )
        self.assertRaises(TypeError, self.set, 'uninitialized_str', 123)
        self.assertEqual(self.set('uninitialized_str', 'value'), 'value')

    def test_initialized_untyped(self):
        """Test access to initialized untyped attribute.

        Untyped attributes can be read, but cannot be written to.
        Gating attribute reads via dataclass fields membership is expensive and
        is not needed anyway.
        """
        self.assertEqual(self.config.initialized_untyped, 'init_value2')
        with self.assertRaises(AttributeError):
            self.config.initialized_untyped = 'new_value'

    def test_union_type(self):
        """Test assignment to Union attributes."""
        self.config.union_str_or_none = 'value'
        self.assertEqual(self.config.union_str_or_none, 'value')
        self.config.union_str_or_none = None
        self.assertIsNone(self.config.union_str_or_none)
        with self.assertRaises(TypeError):
            self.config.union_str_or_none = 1  # ty: ignore[invalid-assignment]

    def test_set_from_str(self):
        """Test attribute type conversion from strings."""
        # Invalid value type: only str supported
        self.assertRaises(
            TypeError, self.config.set_from_str, 'type_conversion_int', 123
        )
        # Supported conversion, from str to int
        self.assertEqual(self.set_from_str('type_conversion_int', '123'), 123)
        # Supported conversion, from str to pathlib.PosixPath
        self.assertEqual(
            self.set_from_str('type_conversion_posixpath', '/path/'),
            pathlib.PosixPath('/path/'),
        )
        # Supported conversion, from str to list
        self.assertEqual(
            self.set_from_str('type_conversion_list', '1 2 2 3 4'),
            ['1', '2', '2', '3', '4'],
        )
        # Supported conversion, from str to set
        self.assertEqual(
            self.set_from_str('type_conversion_set', '1 2 2 3 4'),
            {'1', '2', '3', '4'},
        )
        # Supported conversion, from str to parametrized list
        self.assertEqual(
            self.set_from_str('parametrized_list', '1 2'),
            ['1', '2'],
        )
        # Unsupported conversion, from str to parametrized dict
        self.assertRaises(
            TypeError, self.config.set_from_str, 'parametrized_dict', 'key'
        )
        # Assignment, str to str
        self.assertEqual(self.set_from_str('initialized_str', '123'), '123')
        # Assignment, list converted from str
        self.assertEqual(self.set_from_str('conversion', '1'), ['1'])
        # Unsupported conversion, from str to float
        self.assertRaises(
            TypeError,
            self.config.set_from_str,
            'type_conversion_float',
            '42.0',
        )
        # Assign non-existing attribute
        self.assertRaises(
            AttributeError, self.config.set_from_str, 'unknownattribute', '123'
        )

    def test_append_from_str(self):
        """Test attribute type conversion and appending from strings."""
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
        # Appending, str to list
        self.assertEqual(
            self.set_from_str('type_conversion_list', '1 2'),
            ['1', '2'],
        )
        self.assertEqual(
            self.append_from_str('type_conversion_list', '2 3'),
            ['1', '2', '2', '3'],
        )
        # Appending, str to set
        self.assertEqual(
            self.set_from_str('type_conversion_set', '1 2'),
            {'1', '2'},
        )
        self.assertEqual(
            self.append_from_str('type_conversion_set', '2 3'),
            {'1', '2', '3'},
        )
        # Appending, str to parametrized list
        self.assertEqual(
            self.set_from_str('parametrized_list', '1 2'),
            ['1', '2'],
        )
        self.assertEqual(
            self.append_from_str('parametrized_list', '2 3'),
            ['1', '2', '2', '3'],
        )
        # Unsupported append, from str to parametrized dict
        self.assertRaises(
            TypeError,
            self.config.append_from_str,
            'parametrized_dict',
            'key',
        )
        # Unsupported append, from str to int
        self.assertRaises(
            TypeError, self.append_from_str, 'type_conversion_int', '1'
        )
        # Append non-existing attribute
        self.assertRaises(
            AttributeError, self.append_from_str, 'unknownattribute', '123'
        )

    def test_validation(self):
        """Test attribute metadata validation."""
        self.assertRaises(ValueError, self.set, 'validation', '')
        self.assertEqual(self.set('validation', 'test'), 'test')

    def test_iter(self):
        """Test dataclass field names iteration."""
        self.assertEqual(
            sorted(self.config),
            [
                'conversion',
                'initialized_str',
                'parametrized_dict',
                'parametrized_list',
                'parametrized_union',
                'type_conversion_float',
                'type_conversion_int',
                'type_conversion_list',
                'type_conversion_posixpath',
                'type_conversion_set',
                'uninitialized_str',
                'union_str_or_none',
                'validation',
            ],
        )

    def test_contains(self):
        """Test dataclass field name membership."""
        self.assertIn('initialized_str', self.config)
        self.assertNotIn('unknown_attribute', self.config)

    def test_get(self):
        """Test get() attribute lookup."""
        self.assertEqual(self.config.get('initialized_str'), 'init_value1')
        self.assertEqual(self.config.get('unknown_attribute'), None)
