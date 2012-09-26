from datetime import date, datetime
import pandas as pd
from pivots.millis import unix_time_millis


def get_chart(pivot, rows, cols, values, charts):
    '''
    Get dictionary from pivot suitable for Highcharts.com
     Arguments are the same as to pivots.pivot_table

     Charts is a dict value->chart_type, where chart type is one of highcharts
     types.

    :param pivot: dataframe
    :param rows:
    :param cols:
    :param values:
    :param charts:
    :return: highcharts dictionary
    '''
    xaxis = get_axes(pivot.index, rows, xaxis=True)
    yaxis = get_axes(pivot.columns, values, xaxis=False)

    series = get_series(pivot, yaxis, charts)

    return {
        'xAxis': xaxis,
        'yAxis': yaxis,
        'series': series,
    }


def get_series(table, yaxis, charts=None):
    charts = charts or {}
    series = []
    axis = _axis_names(yaxis)
    for i, column in enumerate(table.columns):
        name = column[0] if isinstance(column, tuple) else column
        serie = {
            'name': ' / '.join(column) if isinstance(column,
                                                     tuple) else column,
            'data': _serialize(table[column]),
            'type': charts.get(name, 'column')
        }

        if isinstance(yaxis, list) and len(yaxis) > 1:
            axis_index = axis.index(name)
            if axis_index >= 0:
                serie['yAxis'] = axis_index
        series.append(serie)
    return series


def get_axes(index, names, xaxis=False):
    axes = []
    for i, name in enumerate(_sanitize_list(names)):
        axis = {
            'title': {
                'text': '_'.join(reversed(name)) if isinstance(name,
                                                               tuple) else name
            },
        }
        if xaxis:
            if isinstance(index, pd.DatetimeIndex):
                axis['type'] = 'datetime'
            else:
                axis['categories'] = [a for a in index]

        if not xaxis and i > 0:
            axis['opposite'] = True
            axis['gridLineWidth'] = 0

        axes.append(axis)

    return axes[0] if len(axes) == 1 else axes


def _serialize(serie):
    ret = []
    for x, y in zip(serie.index, serie):
        if isinstance(x, (date, datetime)):
            x = unix_time_millis(x)
        if pd.np.isnan(y):
            y = 0

        if isinstance(x, basestring):
            ret.append(y)
        else:
            ret.append((x, y))
    return ret


def _axis_names(axis):
    if isinstance(axis, list):
        return [a.get('title', {}).get('text') for a in axis]
    return []


def _sanitize_list(_list):
    if isinstance(_list, list):
        return _list
    return [_list]
