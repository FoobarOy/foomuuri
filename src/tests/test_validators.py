"""Basic unit tests of Validators."""
# pylint: disable=import-error

import unittest

from foomuuri import Validators


class TestValidators(unittest.TestCase):
    """Test assert helpers."""
    def test_assert_str_word(self):
        """Test invalid and valid outcomes."""
        self.assertFalse(Validators.str_zone_name(''))
        self.assertFalse(Validators.str_zone_name('word word'))
        self.assertFalse(Validators.str_zone_name('3word'))
        self.assertFalse(Validators.str_zone_name('w#ord'))
        self.assertTrue(Validators.str_zone_name('wo_123_rd'))
        self.assertTrue(Validators.str_zone_name('_./'))

        self.assertFalse(Validators.str_words(''))
        self.assertTrue(Validators.str_words('word'))
        self.assertTrue(Validators.str_words('word word'))

        self.assertFalse(Validators.int_positive_or_zero(-1))
        self.assertTrue(Validators.int_positive_or_zero(0))
        self.assertTrue(Validators.int_positive_or_zero(1))

        self.assertFalse(Validators.int_positive(-1))
        self.assertTrue(Validators.int_positive(1))

        self.assertFalse(Validators.str_yes_no(''))
        self.assertFalse(Validators.str_yes_no('maybe'))
        self.assertTrue(Validators.str_yes_no('yes'))
        self.assertTrue(Validators.str_yes_no('YES'))
        self.assertTrue(Validators.str_yes_no('no'))
        self.assertTrue(Validators.str_yes_no('NO'))
