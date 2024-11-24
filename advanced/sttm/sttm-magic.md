Have all the SQL statements/sql outputs for more than 10+ jobs that have run in sequence are lumped together in one
file. The sql output has lots of random text detailing the action or logic performed, etc.. before and possibly after
the actual sql statements. The sql could be delete insert, select, merge etc., you can skip delete statements.

Use Select, insert, update, create or replace table merge - in the case of snowflake.
the table name could be prefixed with database name like database.table,
could be prefixed with warehouse and database like warehouse.database.table or database.schema.table

Note that the sql statements are going to be complex with select into happening by joining in multiple tables with case
statements, nested queries, it can have cTE’s as well and so on

Is there a library in python to create source to target mapping random sql statements in a file and it figure out which
table is source and which table is target

if not :
First step extract all the distinct table names and generate a source to target mapping csv file for the tables .

Can we create node and edge files for aws neptune, node label same as table name and edge label to-target

Create a complete solution for source to target mapping
