from datetime import datetime, date
from unittest import TestCase
import pandas as pd
from pivots.highcharts import get_axes, get_series
from pivots.millis import unix_time_millis


class HighchartsPivotTest(TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            [
                (datetime(2010, 1, 1), 'man', 'BA', 1, 2),
                (datetime(2010, 2, 1), 'man', 'KE', 1, 2),
                (datetime(2010, 1, 1), 'woman', 'BA', 1, 2)
            ],
            columns=['month', 'gender', 'town', 'price', 'count']
        )

    def test_one_dimension(self):
        pivot = pd.pivot_table(self.df, rows='month', cols='gender',
                               values='price')

        xaxis = get_axes(pivot.index, 'month', xaxis=True)
        yaxis = get_axes(pivot.columns, 'price')

        self.assertEquals('month', xaxis.get('title', {}).get('text'))
        self.assertEquals('datetime', xaxis.get('type'))

        self.assertEquals('price', yaxis.get('title', {}).get('text'))
        self.assertIsNone(yaxis.get('type'))

    def test_two_dimension(self):
        pivot = pd.pivot_table(self.df, rows='month', cols=['gender'],
                               values=['price', 'count'])

        xaxis = get_axes(pivot.index, 'month', xaxis=True)
        yaxis = get_axes(pivot.columns, ['price', 'count'])

        self.assertEquals('month', xaxis.get('title', {}).get('text'))
        self.assertEquals('datetime', xaxis.get('type'))

        self.assertIsInstance(yaxis, list)
        [price, count] = yaxis

        self.assertEquals('price', price.get('title', {}).get('text'))
        self.assertEquals('count', count.get('title', {}).get('text'))

    def test_two_columns(self):
        pivot = pd.pivot_table(self.df, rows='month', cols=['town', 'gender'],
                               values='price')

        yaxis = get_axes(pivot.columns, 'price')

        self.assertEquals('price', yaxis.get('title', {}).get('text'))

    def test_two_columns_two_dimensions(self):
        pivot = pd.pivot_table(self.df, rows='month', cols=['town', 'gender'],
                               values=['price', 'count'])

        yaxis = get_axes(pivot.columns, ['price', 'count'])
        self.assertIsInstance(yaxis, list)

        [price, count] = yaxis
        self.assertEquals('price', price.get('title', {}).get('text'))
        self.assertEquals('count', count.get('title', {}).get('text'))

    def test_series(self):
        pivot = pd.pivot_table(self.df, rows='month', cols='gender',
                               values='price')

        [man, woman] = get_series(pivot, [])
        self.assertEquals('man', man['name'])
        self.assertEquals([(unix_time_millis(date(2010, 1, 1)), 1.0),
                           (unix_time_millis(date(2010, 2, 1)), 1.0)],
                          man['data'])

        self.assertEquals('woman', woman['name'])
        self.assertEquals([(unix_time_millis(date(2010, 1, 1)), 1.0),
                           (unix_time_millis(date(2010, 2, 1)), 0)],
                          woman['data'])

    def test_series_nondate(self):
        pivot = pd.pivot_table(self.df, rows='gender', cols='town',
                               values='price')

        xaxis = get_axes(pivot.index, 'gender', xaxis=True)
        yaxis = get_axes(pivot.columns, 'price')

        self.assertEquals('gender', xaxis.get('title', {}).get('text'))
        self.assertEquals(['man', 'woman'], xaxis.get('categories', ))

        self.assertIsNone(xaxis.get('type'))
        self.assertEquals('price', yaxis.get('title', {}).get('text'))

        [ba, ke] = get_series(pivot, yaxis)
        self.assertEquals('BA', ba['name'])
        self.assertEquals([1, 1], ba['data'])
        self.assertEquals(None, ba.get('yAxis'))

        self.assertEquals('KE', ke['name'])
        self.assertEquals([1, 0], ke['data'])
        self.assertEquals(None, ke.get('yAxis'))

    def test_axis(self):
        pivot = pd.pivot_table(self.df, rows='gender', cols='town',
                               values=['price', 'count'])

        xaxis = get_axes(pivot.index, 'gender', xaxis=True)
        yaxis = get_axes(pivot.columns, ['price', 'count'])

        self.assertEquals('gender', xaxis.get('title', {}).get('text'))
        self.assertEquals(['man', 'woman'], xaxis.get('categories', ))

        self.assertIsNone(xaxis.get('type'))
        [price, count] = yaxis
        self.assertEquals('price', price.get('title', {}).get('text'))
        self.assertEquals('count', count.get('title', {}).get('text'))

        [price_ba, price_ke, count_ba, count_ke] = get_series(pivot, yaxis)
        self.assertEquals(0, price_ba.get('yAxis'))
        self.assertEquals('price / BA', price_ba.get('name'))
        self.assertEquals(0, price_ke.get('yAxis'))
        self.assertEquals('price / KE', price_ke.get('name'))

        self.assertEquals(1, count_ba.get('yAxis'))
        self.assertEquals('count / BA', count_ba.get('name'))
        self.assertEquals(1, count_ke.get('yAxis'))
        self.assertEquals('count / KE', count_ke.get('name'))

    def test_axis_no_columns(self):
        pivot = pd.pivot_table(self.df, rows='gender',
                               values=['price', 'count'])

        xaxis = get_axes(pivot.index, 'gender', xaxis=True)
        yaxis = get_axes(pivot.columns, ['price', 'count'])

        self.assertEquals('gender', xaxis.get('title', {}).get('text'))
        self.assertEquals(['man', 'woman'], xaxis.get('categories', ))

        self.assertIsNone(xaxis.get('type'))
        [price, count] = yaxis
        self.assertEquals('price', price.get('title', {}).get('text'))
        self.assertEquals('count', count.get('title', {}).get('text'))

        [count, price] = get_series(pivot, yaxis)
        self.assertEquals(0, price.get('yAxis'))
        self.assertEquals('price', price.get('name'))

        self.assertEquals(1, count.get('yAxis'))
        self.assertEquals('count', count.get('name'))

    def test_chart_type(self):
        pivot = pd.pivot_table(self.df, rows='gender',
                               values=['price', 'count'])

        xaxis = get_axes(pivot.index, 'gender', xaxis=True)
        yaxis = get_axes(pivot.columns, ['price', 'count'])

        [count, price] = get_series(pivot, yaxis,
                                    {'count': 'spline', 'price': 'line'})
        self.assertEquals('line', price.get('type'))
        self.assertEquals('spline', count.get('type'))
