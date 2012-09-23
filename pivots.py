import collections
from functools import partial
import sqlalchemy
import pandas as pd


def pivot_table(data, rows, cols, values, aggfunc):
    columns = _column_names(rows, cols, _aggr_column_names(values))

    if data:
        df = pd.DataFrame(data, columns=columns)

        pivot = df.pivot_table(rows=rows, cols=cols, values=values,
                               aggfunc=aggfunc)
        return pivot


def pivot_table_from_select(select, rows, cols, values):
    data = pivot_data(select, rows, cols, values)
    values = _aggr_column_names(values)
    aggfunc = 'mean'
    return pivot_table(data, rows, cols, values, aggfunc)


def pivot_data(select, rows, cols, values):
    '''
    Get aggregated data for pivot table.

    Data will be aggregated like:

    select rows, cols, values from (
        select
    )
    group by rows, cols

    Rows and cols are either string or list of strings.

    Values can be:
    - string
    - list of strings
    - tuple ('aggregation function', column_nane)
    - list of tuples

    All strings are column names in the select.

    Aggregation function is a string one of:
    - sum, count, avg, stddev etc...

    :param executor: sqlalchemy engine, connection or session
    :param select: select providing the data, which will be further aggregated
    :param rows: group columns as rows
    :param cols: group columns as columns
    :param values: aggregated columns
    :return:
    '''
    rows = _sanitize_list(rows)
    cols = _sanitize_list(cols)
    values = _sanitize_list(values)

    rows_columns = _columns(select, rows)
    cols_columns = _columns(select, cols)
    values_columns = _aggr_columns(select, values)

    group_columns = rows_columns + cols_columns
    columns = group_columns + values_columns
    pivot_select = sqlalchemy.select(columns).group_by(*group_columns)

    data = pivot_select.execute(bind=select.bind).fetchall()
    return map(tuple, data)


def _sanitize_list(wannabe_list):
    return wannabe_list if isinstance(wannabe_list, list) else [wannabe_list]


def _column(select, column_name):
    return select.c[column_name]


def _columns(select, column_names):
    return map(partial(_column, select), column_names)


def _aggr_column_name(name):
    func_name = 'sum'
    if isinstance(name, tuple):
        func_name, name = name

    return name, func_name


def _sql_aggregate_function(func_name):
    functions = {len: sqlalchemy.func.count}

    if func_name in functions:
        return functions[func_name]

    return getattr(sqlalchemy.func, func_name)


def _aggr_columns(select, column_names):
    def _aggr_column(name):
        name, func_name = _aggr_column_name(name)

        column = _column(select, name)
        func = _sql_aggregate_function(func_name)
        aggregate = func(column)

        if isinstance(column.type, sqlalchemy.Numeric):
            aggregate = sqlalchemy.cast(aggregate, sqlalchemy.Float)

        return aggregate

    return map(_aggr_column, column_names)


def _aggr_column_names(values):
    functions = map(_aggr_column_name, _sanitize_list(values))

    d = collections.defaultdict(list)
    for name, func_name in functions:
        d[name].append(func_name)


    def a():
        for name in _make_unique(name for name, func_name in functions):
            _functions = d[name]
            if len(_functions) > 1:
                for function in _functions:
                    yield '%s_%s' % (name, function)
            else:
                yield name

    return list(a())


def _column_names(rows, cols, values):
    rows = _sanitize_list(rows)
    cols = _sanitize_list(cols)
    values = _sanitize_list(values)
    return rows + cols + values


def _make_unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]
