pandas-sqlalchemy-pivot
================

Provides pivot functionality for databases. Pivot aggregates are created
directly in the database. Reshaping into pivot is done in the pandas framework.

== Usage ==
select = sqlalchemy.select(table.c.yearmonth, table.c.gender, table.c.price)

table = pivots.pivot_table_from_select(
            select,
            rows='yearmonth', cols='gender', values='price'
        )

print table

=== Output ===
            price
gender     female  male
yearmonth
201001         10    15',


For more examples look at tests.
