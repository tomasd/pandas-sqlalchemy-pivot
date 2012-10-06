pandas-sqlalchemy-pivot
================

Provides pivot functionality for databases. Pivot aggregates are created
directly in the database. Reshaping into pivot is done in the pandas framework.

Usage
=====
    table.insert().execute(customer_id=1, yearmonth='201001', gender='male', price=10)
    table.insert().execute(customer_id=2, yearmonth='201001', gender='male', price=5)
    table.insert().execute(customer_id=3, yearmonth='201001', gender='female', price=10)

    select = sqlalchemy.select(table.c.yearmonth, table.c.gender, table.c.price)

    table = pivots.pivot_table_from_select(
                select,
                rows='yearmonth', cols='gender', values='price'
            )

    print table

Outputs:

                price
    gender     female  male
    yearmonth
    201001         10    15


For more examples look at tests.

Similar projects
================
Similar project for postgresql is Mali Akmanalp's https://github.com/makmanalp/sqlalchemy-crosstab-postgresql