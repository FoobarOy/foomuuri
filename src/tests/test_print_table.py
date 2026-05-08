"""Basic unit tests of print_table()."""
# pylint: disable=invalid-name,import-error
# ruff: noqa: W291

import io
import unittest
import unittest.mock

from foomuuri import print_table


@unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
class TestPrintTable(unittest.TestCase):
    """Test print_table()."""

    def setUp(self):
        """Fill in common fixture values."""
        self.data_multiple_rows = [
            (
                'row 1 column 1',
                'row 1 colum 2',
                'row 1 colu 3',
            ),
            (
                'row 2 colu 1',
                'row 2 colum 2',
                'row 2 column 3',
            ),
        ]

        self.data_no_rows = []

        self.header = (
            'Header',
            'Long Elaborate Header',
            'Medium Header',
        )

    def test_invalid_align_values(self, _):
        """Test invalid align values."""
        invalid_align = [
            '',  # no alignment
            'x',  # invalid align value
            '<<',  # too few values for 3 columns
            '<<<<',  # too much values for 3 columns
        ]

        for align in invalid_align:
            with self.subTest(align):
                self.assertRaises(
                    ValueError,
                    print_table,
                    self.data_multiple_rows,
                    align=align,
                )

    def test_print_table_all_args(self, stdout: io.StringIO):
        """Test table with all supported arguments."""
        print_table(
            data=[self.header] + self.data_multiple_rows,
            header=True,
            align='<>^',
            sep='    ',
        )

        self.assertEqual(
            stdout.getvalue(),
            """Header            Long Elaborate Header    Medium Header 
--------------    ---------------------    --------------
row 1 column 1            row 1 colum 2     row 1 colu 3 
row 2 colu 1              row 2 colum 2    row 2 column 3
""",
        )

    def test_print_table_with_rows_no_headers(self, stdout: io.StringIO):
        """Test table without headers, rows only."""
        print_table(data=self.data_multiple_rows)

        self.assertEqual(
            stdout.getvalue(),
            """row 1 column 1   row 1 colum 2   row 1 colu 3  
row 2 colu 1     row 2 colum 2   row 2 column 3
""",
        )

    def test_print_table_no_rows(self, stdout: io.StringIO):
        """Test table without headers and rows."""
        print_table(data=self.data_no_rows)

        self.assertEqual(
            stdout.getvalue(),
            '',
        )

    def test_print_table_with_headers_no_rows(self, stdout: io.StringIO):
        """Test table with headers, without rows."""
        print_table(data=[self.header] + self.data_no_rows, header=True)
        self.assertEqual(
            stdout.getvalue(),
            '',
        )

    def test_print_table_default_align(self, stdout: io.StringIO):
        """Test table with headers, and default (left) align."""
        print_table(data=[self.header] + self.data_multiple_rows, header=True)

        self.assertEqual(
            stdout.getvalue(),
            """Header           Long Elaborate Header   Medium Header 
--------------   ---------------------   --------------
row 1 column 1   row 1 colum 2           row 1 colu 3  
row 2 colu 1     row 2 colum 2           row 2 column 3
""",
        )
