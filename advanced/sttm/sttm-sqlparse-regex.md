
While `sqlparser` (and similar libraries like `sqlglot` or `sql-metadata`) are available, they each have limitations
when dealing with complex enterprise SQL scenarios. 

```python
import sqlparse
from sqlparse.sql import TokenList
from sqlparse.tokens import Token, Keyword, DML, DDL
import re
from collections import defaultdict
import csv
import json


class SQLLineageParserWithSQLParse:
    def __init__(self):
        self.source_tables = set()
        self.target_tables = set()
        self.lineage_map = defaultdict(set)

    def extract_tables_from_token_list(self, token_list):
        """Extract table names from a SQL tokens list."""
        tables = []
        for token in token_list.tokens:
            if isinstance(token, TokenList):
                tables.extend(self.extract_tables_from_token_list(token))
            # Check for table names after FROM, JOIN, INTO keywords
            elif token.ttype is Keyword and token.value.upper() in ('FROM', 'JOIN', 'INTO'):
                idx = token_list.token_index(token)
                next_token = token_list.token_next(idx)[1]
                if next_token and not next_token.is_whitespace:
                    tables.append(str(next_token))
        return tables

    def process_sql_with_parser(self, sql):
        """Process SQL using sqlparse library."""
        try:
            # Parse the SQL statement
            parsed = sqlparse.parse(sql)

            for statement in parsed:
                # Get statement type
                stmt_type = statement.get_type()

                if stmt_type in ('INSERT', 'UPDATE', 'MERGE', 'CREATE'):
                    # For DML/DDL statements, first token after keyword is usually target
                    for token in statement.tokens:
                        if isinstance(token, TokenList):
                            if token.tokens[0].ttype in (DML, DDL):
                                # Find target table
                                idx = 0
                                while idx < len(token.tokens):
                                    if token.tokens[idx].value.upper() in ('INTO', 'TABLE'):
                                        target = str(token.tokens[idx + 2])
                                        self.target_tables.add(target.strip('` "'))
                                        break
                                    idx += 1

                # Extract all potential source tables
                sources = self.extract_tables_from_token_list(statement)
                self.source_tables.update(sources)

        except Exception as e:
            print(f"Error parsing SQL with sqlparse: {e}")
            # Fallback to regex-based parsing
            return self.process_sql_with_regex(sql)

    def process_sql_with_regex(self, sql):
        """Fallback regex-based processing for complex cases sqlparse can't handle."""
        # Original regex-based implementation as backup
        sql = sql.lower()

        # Extract target tables
        patterns = {
            'merge': r'merge\s+into\s+([^\s(]+)',
            'insert': r'insert\s+into\s+([^\s(]+)',
            'create': r'create\s+(?:or\s+replace\s+)?table\s+([^\s(]+)',
            'update': r'update\s+([^\s(]+)'
        }

        for pattern in patterns.values():
            matches = re.finditer(pattern, sql)
            self.target_tables.update(m.group(1).strip('` "') for m in matches)

        # Extract source tables
        from_pattern = r'from\s+([^\s(]+)|join\s+([^\s(]+)'
        matches = re.finditer(from_pattern, sql)
        self.source_tables.update(
            m.group(1) if m.group(1) else m.group(2).strip('` "')
            for m in matches
        )

    def process_sql_statement(self, sql):
        """Process a single SQL statement using both parsers."""
        # Try sqlparse first
        self.process_sql_with_parser(sql)

        # Update lineage map
        for target in self.target_tables:
            self.lineage_map[target].update(self.source_tables)

    def process_sql_file(self, file_path):
        """Process SQL file and build lineage."""
        with open(file_path, 'r') as f:
            sql_content = f.read()

        # Split into individual SQL statements
        statements = sqlparse.split(sql_content)

        for stmt in statements:
            if stmt.strip():
                self.process_sql_statement(stmt)


# Example usage showing limitations
def demonstrate_parser_limitations():
    # Complex SQL that might challenge sqlparse
    complex_sql = """
    -- Complex MERGE statement with CTE
    WITH updated_records AS (
        SELECT t1.*, t2.col2 
        FROM database1.schema1.table1 t1
        LEFT JOIN database2.schema2.table2 t2 ON t1.id = t2.id
        WHERE EXISTS (
            SELECT 1 FROM database3.schema3.table3 t3
            WHERE t3.id = t1.id
        )
    )
    MERGE INTO target.schema.final_table AS target
    USING (
        SELECT * FROM updated_records
        UNION ALL
        SELECT * FROM database4.schema4.table4
        WHERE condition = 'complex'
    ) AS source
    ON target.id = source.id
    WHEN MATCHED THEN UPDATE SET target.col1 = source.col1
    WHEN NOT MATCHED THEN INSERT (col1, col2) VALUES (source.col1, source.col2);
    """

    parser = SQLLineageParserWithSQLParse()

    print("Processing with SQLParse:")
    parser.process_sql_statement(complex_sql)
    print("\nDetected source tables:", parser.source_tables)
    print("Detected target tables:", parser.target_tables)

    # Now try with just regex
    parser = SQLLineageParserWithSQLParse()
    print("\nProcessing with regex fallback:")
    parser.process_sql_with_regex(complex_sql)
    print("\nDetected source tables:", parser.source_tables)
    print("Detected target tables:", parser.target_tables)


if __name__ == "__main__":
    demonstrate_parser_limitations()

```

Here's why using just `sqlparse` (or similar SQL parsing libraries) can be challenging for enterprise SQL:

1. Limited Support for Complex Syntax:
    - Many SQL parsers struggle with vendor-specific syntax (like Snowflake's CREATE OR REPLACE)
    - Complex MERGE statements with multiple conditions can be parsed incorrectly
    - CTEs with multiple levels of nesting can cause parsing errors

2. Dialect Differences:
    - Enterprise environments often use specific SQL dialects (Snowflake, Redshift, etc.)
    - Most SQL parsers are built for standard ANSI SQL
    - Custom functions and syntax extensions aren't recognized

3. Performance Issues:
    - Full SQL parsing can be computationally expensive for very large SQL files
    - Memory usage can spike when parsing complex nested queries

4. Error Recovery:
    - SQL parsers often fail completely when encountering unexpected syntax
    - No partial results are returned if parsing fails

That's why the solution I provided uses a hybrid approach:

1. Tries to use `sqlparse` for basic SQL parsing
2. Falls back to regex-based parsing for complex cases
3. Handles vendor-specific syntax patterns
4. More resilient to syntax variations

However, if you want to use SQL parsers, here are some alternatives worth considering:

1. `sqlglot`: More modern, supports multiple dialects

```python
import sqlglot


def parse_with_sqlglot(sql):
    try:
        parsed = sqlglot.parse_one(sql)
        # Extract tables from AST
        tables = parsed.find_all(sqlglot.exp.Table)
    except:
        # Fallback to regex
        pass
```

2. `sql-metadata`: Specifically designed for metadata extraction

```python
from sql_metadata import Parser


def parse_with_sql_metadata(sql):
    try:
        parser = Parser(sql)
        tables = parser.tables
    except:
        # Fallback to regex
        pass
```
