from decimal import Decimal
from unittest import TestCase
import sqlalchemy
import pivots


class PivotTest(TestCase):
    def setUp(self):
        self.engine = sqlalchemy.create_engine('sqlite://', echo=False)
        self.metadata = sqlalchemy.MetaData(bind=self.engine)

        self.mytable = sqlalchemy.Table(
            'mytable', self.metadata,
            sqlalchemy.Column('customer_id', sqlalchemy.Integer),
            sqlalchemy.Column('yearmonth', sqlalchemy.String(50)),
            sqlalchemy.Column('gender', sqlalchemy.String(50)),
            sqlalchemy.Column('town', sqlalchemy.String(50)),
            sqlalchemy.Column('price', sqlalchemy.Numeric),
        )
        self.metadata.create_all(bind=self.engine, checkfirst=False)

    def _insert_data(self, customer_id, yearmonth, gender, price, town=None):
        self.mytable.insert().execute(
            customer_id=customer_id,
            yearmonth=yearmonth,
            gender=gender,
            price=price,
            town=town
        )

    def test_pivot_data(self):
        self._insert_data(1, '201001', 'male', 10)
        self._insert_data(2, '201001', 'male', 5)
        self._insert_data(3, '201001', 'female', 10)

        select = self.mytable.select().order_by('yearmonth', 'gender')
        data = pivots.pivot_data(
            select,
            rows='yearmonth', cols='gender', values='price'
        )

        self.assertEquals(
            [
                (u'201001', u'female', 10),
                (u'201001', u'male', 15)
            ],
            data
        )

    def test_pivot_table(self):
        self._insert_data(1, '201001', 'male', 10)
        self._insert_data(2, '201001', 'male', 5)
        self._insert_data(3, '201001', 'female', 10)

        select = self.mytable.select().order_by('yearmonth', 'gender')
        table = pivots.pivot_table_from_select(
            select,
            rows='yearmonth', cols='gender', values='price'
        )

        self.assertEquals('            price      \n'
                          'gender     female  male\n'
                          'yearmonth              \n'
                          '201001         10    15', str(table))

    def test_avg(self):
        self._insert_data(1, '201001', 'male', 10)
        self._insert_data(2, '201001', 'male', 5)
        self._insert_data(3, '201001', 'female', 10)

        table = pivots.pivot_table_from_select(
            self.mytable.select(),
            rows='yearmonth', cols='gender', values=('avg', 'price')
        )

        self.assertEquals(10, table.price.female['201001'])
        self.assertEquals(7.5, table.price.male['201001'])

    def test_count(self):
        self._insert_data(1, '201001', 'male', 10)
        self._insert_data(2, '201001', 'male', 5)
        self._insert_data(3, '201001', 'female', 10)

        table = pivots.pivot_table_from_select(
            self.mytable.select(),
            rows='yearmonth', cols='gender', values=('count', 'price')
        )

        self.assertEquals(1, table.price.female['201001'])
        self.assertEquals(2, table.price.male['201001'])

    def test_empty(self):
        table = pivots.pivot_table_from_select(
            self.mytable.select(),
            rows='yearmonth', cols='gender', values='price'
        )

        self.assertIsNone(table)

    def test_len(self):
        self._insert_data(1, '201001', 'male', 10)
        self._insert_data(2, '201001', 'male', 5)
        self._insert_data(3, '201001', 'female', 10)

        table = pivots.pivot_table_from_select(
            self.mytable.select(),
            rows='yearmonth', cols='gender', values=(len, 'price')
        )

        self.assertEquals(1, table.price.female['201001'])
        self.assertEquals(2, table.price.male['201001'])

    def test_multiple_columns(self):
        self._insert_data(1, '201001', 'male', 10, town='BA')
        self._insert_data(2, '201001', 'male', 5, town='KE')
        self._insert_data(3, '201001', 'female', 10, town='BA')

        table = pivots.pivot_table_from_select(
            self.mytable.select(),
            rows='yearmonth', cols=['town', 'gender'], values=(len, 'price')
        )

        self.assertEquals(1, table.price.BA.female['201001'])
        self.assertEquals(1, table.price.BA.male['201001'])
        self.assertEquals(1, table.price.KE.male['201001'])

    def test_multiple_functions(self):
        self._insert_data(1, '201001', 'male', 10)
        self._insert_data(2, '201001', 'male', 5)
        self._insert_data(3, '201001', 'female', 10)

        table = pivots.pivot_table_from_select(
            self.mytable.select(),
            rows='yearmonth', cols='gender',
            values=[('count', 'price'), ('sum', 'price')]
        )

        self.assertEquals(2, table.price_count.male['201001'])
        self.assertEquals(1, table.price_count.female['201001'])

        self.assertEquals(15, table.price_sum.male['201001'])
        self.assertEquals(10, table.price_sum.female['201001'])

    def test_pivot(self):
        data = [(u'201001', u'male', 10),
                (u'201001', u'male', 5),
                (u'201001', u'female', 10)]

        table = pivots.pivot_table(data,
                           rows='yearmonth',
                           cols='gender',
                           values='price', aggfunc=len)

        self.assertEquals(2, table.male['201001'])
        self.assertEquals(1, table.female['201001'])

        table = pivots.pivot_table(data,
                                   rows='yearmonth',
                                   cols='gender',
                                   values='price', aggfunc={'price':len})

        self.assertEquals(2, table.male['201001'])
        self.assertEquals(1, table.female['201001'])

    def test_decimal(self):
        data = [(u'201001', u'male', Decimal(10)),
                (u'201001', u'male', Decimal(5)),
                (u'201001', u'female', Decimal(10))]

        table = pivots.pivot_table(data,
                                   rows='yearmonth',
                                   cols='gender',
                                   values='price', aggfunc=len)

        self.assertEquals(2, table.male['201001'])
        self.assertEquals(1, table.female['201001'])

        table = pivots.pivot_table(data,
                                   rows='yearmonth',
                                   cols='gender',
                                   values='price', aggfunc={'price':'mean'})

        self.assertEquals(7.5, table.male['201001'])
        self.assertEquals(10, table.female['201001'])
