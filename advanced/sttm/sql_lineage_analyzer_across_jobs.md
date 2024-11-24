Create a Python solution to analyze SQL statements and generate source-to-target mappings, along with
Neptune graph files.

```python
import sqlparse
import re
from collections import defaultdict
import csv
import pandas as pd


class SQLLineageAnalyzer:
    def __init__(self):
        # Store unique source and target tables
        self.source_tables = set()
        self.target_tables = set()
        # Store relationships between tables
        self.relationships = defaultdict(set)

    def extract_table_name(self, table_ref):
        """
        Extract clean table name from various formats:
        - warehouse.database.table
        - database.schema.table
        - database.table
        - table
        Returns the full qualified name
        """
        parts = table_ref.strip().split('.')
        return '.'.join(parts)

    def parse_sql_statement(self, sql):
        """
        Parse individual SQL statement to identify source and target tables
        Returns tuple of (target_tables, source_tables)
        """
        # Parse the SQL statement
        parsed = sqlparse.parse(sql)[0]
        tokens = parsed.tokens

        target_tables = set()
        source_tables = set()

        # Identify statement type
        stmt_type = parsed.get_type().lower()

        if stmt_type == 'insert':
            # Find target table (after INSERT INTO)
            insert_idx = None
            for idx, token in enumerate(tokens):
                if token.value.upper() == 'INSERT':
                    insert_idx = idx
                    break

            if insert_idx is not None:
                # Look for table name after INSERT INTO
                for token in tokens[insert_idx:]:
                    if isinstance(token, sqlparse.sql.Identifier):
                        target_tables.add(self.extract_table_name(token.value))
                        break

            # Find source tables in SELECT part
            select_seen = False
            for token in tokens:
                if token.value.upper() == 'SELECT':
                    select_seen = True
                if select_seen and isinstance(token, sqlparse.sql.Identifier):
                    if '.' in token.value:  # Only add if it looks like a table reference
                        source_tables.add(self.extract_table_name(token.value))

        elif stmt_type == 'update':
            # Find target table (after UPDATE)
            update_idx = None
            for idx, token in enumerate(tokens):
                if token.value.upper() == 'UPDATE':
                    update_idx = idx
                    break

            if update_idx is not None:
                # Look for table name after UPDATE
                for token in tokens[update_idx:]:
                    if isinstance(token, sqlparse.sql.Identifier):
                        target_tables.add(self.extract_table_name(token.value))
                        break

            # Find source tables in FROM/JOIN clauses
            from_seen = False
            for token in tokens:
                if token.value.upper() in ('FROM', 'JOIN'):
                    from_seen = True
                if from_seen and isinstance(token, sqlparse.sql.Identifier):
                    if '.' in token.value:
                        source_tables.add(self.extract_table_name(token.value))

        elif stmt_type == 'create':
            # Handle CREATE TABLE statements
            create_idx = None
            for idx, token in enumerate(tokens):
                if token.value.upper() == 'CREATE':
                    create_idx = idx
                    break

            if create_idx is not None:
                # Look for target table name after CREATE TABLE
                for token in tokens[create_idx:]:
                    if isinstance(token, sqlparse.sql.Identifier):
                        target_tables.add(self.extract_table_name(token.value))
                        break

            # Find source tables in SELECT part if it's CREATE TABLE AS SELECT
            select_seen = False
            for token in tokens:
                if token.value.upper() == 'SELECT':
                    select_seen = True
                if select_seen and isinstance(token, sqlparse.sql.Identifier):
                    if '.' in token.value:
                        source_tables.add(self.extract_table_name(token.value))

        elif stmt_type == 'merge':
            # Handle MERGE statements
            merge_idx = None
            for idx, token in enumerate(tokens):
                if token.value.upper() == 'MERGE':
                    merge_idx = idx
                    break

            if merge_idx is not None:
                # Look for target table after MERGE INTO
                for token in tokens[merge_idx:]:
                    if isinstance(token, sqlparse.sql.Identifier):
                        target_tables.add(self.extract_table_name(token.value))
                        break

            # Find source tables in USING clause
            using_seen = False
            for token in tokens:
                if token.value.upper() == 'USING':
                    using_seen = True
                if using_seen and isinstance(token, sqlparse.sql.Identifier):
                    if '.' in token.value:
                        source_tables.add(self.extract_table_name(token.value))

        return target_tables, source_tables

    def analyze_sql_file(self, file_path):
        """
        Analyze SQL file containing multiple statements
        Updates internal state with found relationships
        """
        with open(file_path, 'r') as f:
            sql_content = f.read()

        # Split into individual statements
        statements = sqlparse.split(sql_content)

        for stmt in statements:
            if stmt.strip():
                # Skip DELETE statements
                if not stmt.strip().upper().startswith('DELETE'):
                    target_tables, source_tables = self.parse_sql_statement(stmt)

                    # Update our collections
                    self.target_tables.update(target_tables)
                    self.source_tables.update(source_tables)

                    # Store relationships
                    for target in target_tables:
                        self.relationships[target].update(source_tables)

    def generate_mapping_csv(self, output_file):
        """
        Generate CSV file with source to target mappings
        """
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Source Table', 'Target Table'])

            for target, sources in self.relationships.items():
                for source in sources:
                    writer.writerow([source, target])

    def generate_neptune_files(self, nodes_file, edges_file):
        """
        Generate node and edge files for AWS Neptune
        """
        # Generate nodes file
        nodes = pd.DataFrame(list(self.source_tables.union(self.target_tables)),
                             columns=['~id'])
        nodes['~label'] = nodes['~id'].apply(lambda x: x.split('.')[-1])  # Use last part as label
        nodes.to_csv(nodes_file, index=False)

        # Generate edges file
        edges_list = []
        for target, sources in self.relationships.items():
            for source in sources:
                edges_list.append({
                    '~id': f"e_{source.replace('.', '_')}_to_{target.replace('.', '_')}",
                    '~from': source,
                    '~to': target,
                    '~label': 'to-target'
                })

        edges_df = pd.DataFrame(edges_list)
        edges_df.to_csv(edges_file, index=False)


def analyze_sql_lineage(sql_file_path, mapping_csv_path, nodes_file_path, edges_file_path):
    """
    Main function to analyze SQL file and generate all outputs
    """
    # Create analyzer instance
    analyzer = SQLLineageAnalyzer()

    # Analyze SQL file
    analyzer.analyze_sql_file(sql_file_path)

    # Generate mapping CSV
    analyzer.generate_mapping_csv(mapping_csv_path)

    # Generate Neptune files
    analyzer.generate_neptune_files(nodes_file_path, edges_file_path)

    return analyzer


# Example usage
if __name__ == "__main__":
    analyzer = analyze_sql_lineage(
        'input_sql_file.sql',
        'table_mappings.csv',
        'neptune_nodes.csv',
        'neptune_edges.csv'
    )

```

I've created a comprehensive solution for analyzing SQL statements and generating source-to-target mappings. Here are
the key features:

1. Uses `sqlparse` library to parse SQL statements
2. Handles multiple SQL statement types:
    - INSERT statements (including INSERT INTO ... SELECT)
    - UPDATE statements
    - CREATE TABLE statements (including CREATE TABLE AS SELECT)
    - MERGE statements (Snowflake syntax)

3. Handles various table name formats:
    - warehouse.database.table
    - database.schema.table
    - database.table
    - Simple table names

4. Generates three types of output:
    - Source-to-target mapping CSV file
    - Neptune nodes file
    - Neptune edges file

Install the required packages:
```bash
pip install sqlparse pandas
```

Run as follows:

```python
analyzer = analyze_sql_lineage(
    'your_sql_file.sql',
    'output_mappings.csv',
    'neptune_nodes.csv',
    'neptune_edges.csv'
)
```
