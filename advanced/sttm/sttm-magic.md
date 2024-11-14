I have lots of SQL statements generated from lots of script thet run a set of processes for a subsystem, these sql
outputs are in various files. the SQL could be delete insert, select, merge etc., you can skip delete statements I will
combine all the files and extract all the distinct table names and generate a source to target mapping csv file for the
tables which use Select, insert, merge - in the case of snowflake
use python - tables as nodes and relation ship between source and target table as edges - id, from ,to - for neptune db 