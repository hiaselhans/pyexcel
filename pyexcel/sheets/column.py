from pyexcel.sheets.filters import ColumnFilter
from . import _shared as utils
from .formatters import ColumnFormatter
import pyexcel._compact as compact


class Column:
    """Represent columns of a matrix

    .. table:: "example.csv"

        = = =
        1 2 3
        4 5 6
        7 8 9
        = = =

    Let us manipulate the data columns on the above data matrix::

        >>> import pyexcel as pe
        >>> data = [[1,2,3], [4,5,6], [7,8,9]]
        >>> m = pe.sheets.Matrix(data)
        >>> m.column[0]
        [1, 4, 7]
        >>> m.column[2] = [0, 0, 0]
        >>> m.column[2]
        [0, 0, 0]
        >>> del m.column[1]
        >>> m.column[1]
        [0, 0, 0]
        >>> m.column[2]
        Traceback (most recent call last):
            ...
        IndexError

    """
    def __init__(self, matrix):
        self.ref = matrix

    def select(self, indices):
        """
        Examples:

            >>> import pyexcel as pe
            >>> data = [[1,2,3,4,5,6,7,9]]
            >>> sheet = pe.Sheet(data)
            >>> sheet
            pyexcel sheet:
            +---+---+---+---+---+---+---+---+
            | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 9 |
            +---+---+---+---+---+---+---+---+
            >>> sheet.column.select([1,2,3,5])
            >>> sheet
            pyexcel sheet:
            +---+---+---+---+
            | 2 | 3 | 4 | 6 |
            +---+---+---+---+

        """
        self.ref.filter(ColumnFilter(indices).invert())

    def __delitem__(self, aslice):
        """Override the operator to delete items

        Examples:

            >>> import pyexcel as pe
            >>> data = [[1,2,3,4,5,6,7,9]]
            >>> sheet = pe.Sheet(data)
            >>> sheet
            pyexcel sheet:
            +---+---+---+---+---+---+---+---+
            | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 9 |
            +---+---+---+---+---+---+---+---+
            >>> del sheet.column[1,2,3,5]
            >>> sheet
            pyexcel sheet:
            +---+---+---+---+
            | 1 | 5 | 7 | 9 |
            +---+---+---+---+

        """
        if isinstance(aslice, slice):
            my_range = utils.analyse_slice(aslice,
                                           self.ref.number_of_columns())
            self.ref.delete_columns(my_range)
        elif isinstance(aslice, str):
            index = utils.excel_column_index(aslice)
            self.ref.delete_columns([index])
        elif isinstance(aslice, tuple):
            indices = list(aslice)
            self.ref.filter(ColumnFilter(indices))
        elif isinstance(aslice, list):
            indices = aslice
            self.ref.filter(ColumnFilter(indices))
        elif isinstance(aslice, int):
            self.ref.delete_columns([aslice])
        else:
            raise IndexError

    def __setitem__(self, aslice, c):
        """Override the operator to set items"""
        if isinstance(aslice, slice):
            my_range = utils.analyse_slice(aslice,
                                           self.ref.number_of_columns())
            for i in my_range:
                self.ref.set_column_at(i, c)
        elif isinstance(aslice, str):
            index = utils.excel_column_index(aslice)
            self.ref.set_column_at(index, c)
        elif isinstance(aslice, int):
            self.ref.set_column_at(aslice, c)
        else:
            raise IndexError

    def __getitem__(self, aslice):
        """By default, this class recognize from top to bottom
        from left to right"""
        index = aslice
        if isinstance(aslice, slice):
            my_range = utils.analyse_slice(aslice,
                                           self.ref.number_of_columns())
            results = []
            for i in my_range:
                results.append(self.ref.column_at(i))
            return results
        elif isinstance(aslice, str):
            index = utils.excel_column_index(aslice)
        if index in self.ref.column_range():
            return self.ref.column_at(index)
        else:
            raise IndexError

    def __iadd__(self, other):
        """Overload += sign

        :return: self
        """
        if isinstance(other, list):
            self.ref.extend_columns(other)
        elif hasattr(other, "_array"):
            self.ref.extend_columns_with_rows(other._array)
        else:
            raise TypeError
        return self

    def __add__(self, other):
        """Overload += sign

        :return: self
        """
        self.__iadd__(other)
        return self.ref


class NamedColumn(Column):
    """Series Sheet would have Named Column instead of Column

    example::

        import pyexcel as pe

        r = pe.SeriesReader("example.csv")
        print(r.column["column 1"])

    """
    def select(self, names):
        """Delete columns other than specified

        Examples:

            >>> import pyexcel as pe
            >>> data = [[1,2,3,4,5,6,7,9]]
            >>> sheet = pe.Sheet(data)
            >>> sheet
            pyexcel sheet:
            +---+---+---+---+---+---+---+---+
            | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 9 |
            +---+---+---+---+---+---+---+---+
            >>> sheet.column.select([1,2,3,5])
            >>> sheet
            pyexcel sheet:
            +---+---+---+---+
            | 2 | 3 | 4 | 6 |
            +---+---+---+---+
            >>> data = [
            ...     ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
            ...     [1,2,3,4,5,6,7,9],
            ... ]
            >>> sheet = pe.Sheet(data, name_columns_by_row=0)
            >>> sheet
            pyexcel sheet:
            +---+---+---+---+---+---+---+---+
            | a | b | c | d | e | f | g | h |
            +===+===+===+===+===+===+===+===+
            | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 9 |
            +---+---+---+---+---+---+---+---+
            >>> del sheet.column['a', 'b', 'i', 'f'] # doctest:+ELLIPSIS
            Traceback (most recent call last):
                ...
            ValueError: ...
            >>> sheet.column.select(['a', 'c', 'e', 'h'])
            >>> sheet
            pyexcel sheet:
            +---+---+---+---+
            | a | c | e | h |
            +===+===+===+===+
            | 1 | 3 | 5 | 9 |
            +---+---+---+---+

        """
        if compact.is_array_type(names, str):
            indices = utils.names_to_indices(names,
                                             self.ref.colnames)
            Column.select(self, indices)
        else:
            Column.select(self, names)

    def __delitem__(self, str_or_aslice):
        """

        Example::

            >>> import pyexcel as pe
            >>> data = [
            ...     ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
            ...     [1,2,3,4,5,6,7,9],
            ... ]
            >>> sheet = pe.Sheet(data, name_columns_by_row=0)
            >>> sheet
            pyexcel sheet:
            +---+---+---+---+---+---+---+---+
            | a | b | c | d | e | f | g | h |
            +===+===+===+===+===+===+===+===+
            | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 9 |
            +---+---+---+---+---+---+---+---+
            >>> del sheet.column['a', 'b', 'i', 'f'] # doctest:+ELLIPSIS
            Traceback (most recent call last):
                ...
            ValueError: ...
            >>> del sheet.column['a', 'c', 'e', 'h']
            >>> sheet
            pyexcel sheet:
            +---+---+---+---+
            | b | d | f | g |
            +===+===+===+===+
            | 2 | 4 | 6 | 7 |
            +---+---+---+---+

        """
        if compact.is_string(type(str_or_aslice)):
            self.ref.delete_named_column_at(str_or_aslice)
        elif compact.is_tuple_consists_of_strings(str_or_aslice):
            indices = utils.names_to_indices(list(str_or_aslice),
                                             self.ref.colnames)
            Column.__delitem__(self, indices)
        else:
            Column.__delitem__(self, str_or_aslice)

    def __setitem__(self, str_or_aslice, c):
        if compact.is_string(type(str_or_aslice)):
            self.ref.set_named_column_at(str_or_aslice, c)
        else:
            Column.__setitem__(self, str_or_aslice, c)

    def __getitem__(self, str_or_aslice):
        if compact.is_string(type(str_or_aslice)):
            return self.ref.named_column_at(str_or_aslice)
        else:
            return Column.__getitem__(self, str_or_aslice)

    def __iadd__(self, other):
        """Overload += sign

        :param list other: the column header must be the first element.
        :return: self
        """
        if isinstance(other, compact.OrderedDict):
            self.ref.extend_columns(other)
        else:
            Column.__iadd__(self, other)
        return self

    def __add__(self, other):
        """Overload += sign

        :return: self
        """
        self.__iadd__(other)
        return self.ref

    def format(self,
               column_index=None, formatter=None,
               format_specs=None):
        """Format a column
        """
        def handle_one_formatter(columns, aformatter):
            new_indices = columns
            if len(self.ref.colnames) > 0:
                new_indices = utils.names_to_indices(columns,
                                                     self.ref.colnames)
            theformatter = ColumnFormatter(new_indices, aformatter)
            self.ref.apply_formatter(theformatter)
        if column_index is not None:
            handle_one_formatter(column_index, formatter)
        elif format_specs:
            for spec in format_specs:
                handle_one_formatter(spec[0], spec[1])
