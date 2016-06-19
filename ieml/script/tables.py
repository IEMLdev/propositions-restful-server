from ieml.script import AdditiveScript, MultiplicativeScript
from collections import namedtuple
import numpy as np

_tables = []
Variable = namedtuple('Variable', ['address', 'script'])
Table = namedtuple('Table', ['headers', 'cells', 'dimension'])


def generate_tables(s):
    """Generates a paradigm table from a given Script.
       The table is implemented using a named tuple"""

    if isinstance(s, AdditiveScript):
        for child in s.children:
            return generate_tables(child)
    elif isinstance(s, MultiplicativeScript):
        plural_vars = [Variable(i, child) for (i, child) in enumerate(s.children) if child.cardinal > 1]
        if len(plural_vars) == 3:  # We build a 3D table
            return _tables.append(build_table(3, s, plural_vars))
        elif len(plural_vars) == 2:  # We build a 2D table
            return _tables.append(build_table(2, s, plural_vars))
        elif len(plural_vars) == 1:  # we build a 1D table
            if plural_vars[0].script.layer == 0:
                return _tables.append(build_table(1, s, plural_vars))
            else:
                return process_tables(generate_tables(plural_vars[0].script), plural_vars[0].address, s)


def process_tables(tables, address, parent_script):
    """Distributes the sibling multiplications on tables headers and cells"""

    new_tables = []

    # TODO: There's gotta be a better  cleaner way godayum
    if address == 0:  # We need to distribute the multiplication of the attribute and mode of the parent Script
        for table in tables:
            headers = [[MultiplicativeScript(script, parent_script.children[1], parent_script.children[2])
                        for script in dimension] for dimension in table.headers]
            if table.cells.ndim == 1:
                cells = np.fromiter(
                    [MultiplicativeScript(script, parent_script.children[1], parent_script.children[2]) for script in
                     table.cells])
            elif table.cells.ndim == 2:
                cells = np.fromiter(
                    [[MultiplicativeScript(script, parent_script.children[1], parent_script.children[2]) for script in
                      row] for row in table.cells])
            elif table.cells.ndim == 3:
                cells = np.fromiter(
                    [[[MultiplicativeScript(script, parent_script.children[1], parent_script.children[2])
                       for script in k] for k in row] for row in table.cells])
            new_tables.append(Table(headers, cells))
    elif address == 1:  # We need to distribute the multiplication of the substance from the right and mode from the left
        for table in tables:
            headers = [[MultiplicativeScript(parent_script.children[0], script, parent_script.children[2])
                        for script in dimension] for dimension in table.headers]
            if table.cells.ndim == 1:
                cells = np.fromiter(
                    [MultiplicativeScript(parent_script.children[0], script, parent_script.children[2]) for script in
                     table.cells])
            elif table.cells.ndim == 2:
                cells = np.fromiter(
                    [[MultiplicativeScript(parent_script.children[0], script, parent_script.children[2]) for script in
                      row] for row in table.cells])
            elif table.cells.ndim == 3:
                cells = np.fromiter(
                    [[[MultiplicativeScript(parent_script.children[0], script, parent_script.children[2])
                       for script in k] for k in row] for row in table.cells])
            new_tables.append(Table(headers, cells))
    elif address == 2:  # We need to distribute the multiplication of the substance and the attribute from the right
        for table in tables:
            headers = [[MultiplicativeScript(parent_script.children[0], parent_script.children[1], script)
                        for script in dimension] for dimension in table.headers]
            if table.cells.ndim == 1:
                cells = np.fromiter(
                    [MultiplicativeScript(parent_script.children[0], parent_script.children[1], script) for script in
                     table.cells])
            elif table.cells.ndim == 2:
                cells = np.fromiter(
                    [[MultiplicativeScript(parent_script.children[0], parent_script.children[1], script) for script in
                      row] for row in table.cells])
            elif table.cells.ndim == 3:
                cells = np.fromiter(
                    [[[MultiplicativeScript(parent_script.children[0], parent_script.children[1], script)
                       for script in k] for k in row] for row in table.cells])
            new_tables.append(Table(headers, cells))

    return new_tables


def build_table(dimension, multi_script, plural_vars):
    """Constructs the paradigm table and returns it"""
    row_headers = []
    col_headers = []
    tab_headers = []

    if dimension == 1:  # In this case
        cells = np.empty(plural_vars[0].script.cardinal, dtype=object)
        row_headers.append(multi_script)
    if dimension >= 2:
        cells = np.empty((plural_vars[0].script.cardinal, plural_vars[1].script.cardinal), dtype=object)
        row_headers = make_headers(plural_vars[0], *multi_script.children)
        col_headers = make_headers(plural_vars[1], *multi_script.children)
    if dimension == 3:
        cells = np.empty((plural_vars[0].script.cardinal, plural_vars[1].script.cardinal, plural_vars[2].script.cardinal), dtype=object)
        tab_headers = make_headers(plural_vars[2], *multi_script.children)

    fill_cells(cells, plural_vars, row_headers, col_headers, tab_headers)
    return Table(headers=[row_headers, col_headers, tab_headers], cells=cells, dimension=dimension)


def fill_cells(cells, plural_vars, row_header, col_header, tab_header):
    """Fills in the cells of the paradigm table by multiplying it's headers"""
    if cells.ndim == 1:
        operands = [row_header[0], row_header[1], row_header[2]]
        for i, child in enumerate(row_header.children):
            operands[plural_vars[0].address] = child
            cells[i] = MultiplicativeScript(*operands)
    elif cells.ndim == 2:
        for i, r_header in enumerate(row_header):
            for j, c_header in enumerate(col_header):
                if plural_vars[0].address == 0 and plural_vars[1].address == 1:
                    cells[i][j] = MultiplicativeScript(substance=r_header[0], attribute=c_header[1], mode=r_header[2])
                    cells[i][j].check()
                elif plural_vars[0].address == 1 and plural_vars[1].address == 2:
                    cells[i][j] = MultiplicativeScript(substance=r_header[0], attribute=r_header[1], mode=c_header[2])
                    cells[i][j].check()
                elif plural_vars[0].address == 0 and plural_vars[1].address == 2:
                    cells[i][j] = MultiplicativeScript(substance=r_header[0], attribute=r_header[1], mode=c_header[2])
                    cells[i][j].check()
    elif cells.ndim == 3:
        for i, r_header in enumerate(row_header):
            for j, c_header in enumerate(col_header):
                for k, t_header in enumerate(tab_header):
                    cells[i][j][k] = MultiplicativeScript(substance=r_header[0], attribute=c_header[1], mode=t_header[2])
                    cells.check()


def make_headers(plural_variable, substance, attribute, mode):
    """Builds the headers for a 2D or 3D paradigm table"""
    operands = [substance, attribute, mode]
    headers = []

    for child in plural_variable.script.children:
        operands[plural_variable.address] = child
        script = MultiplicativeScript(*operands)
        script.check()
        headers.append(script)
    return headers


def print_table(t):
    """Prints out the table for debugging purposes"""
    pass
