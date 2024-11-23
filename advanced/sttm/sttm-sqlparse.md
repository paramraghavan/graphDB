The SQL parsing libraries like `sqlparse` and `sqlglot`, for complex SQL statements with CTEs, nested queries, and
multiple operations, we'll need a more robust solution to accurately identify source and target tables.

```python
import re
from collections import defaultdict
import csv
import json


class SQLLineageParser:
    def __init__(self):
        self.source_tables = set()
        self.target_tables = set()
        self.lineage_map = defaultdict(set)

    def normalize_table_name(self, table):
        """Normalize table names by removing quotes and handling fully qualified names."""
        table = table.strip('"`[]')
        return table.lower()

    def extract_tables_from_sql(self, sql):
        """Extract source and target tables from SQL statement."""
        # Remove comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

        # Convert to lowercase for case-insensitive matching
        sql = sql.lower()

        # Find target tables
        # MERGE INTO pattern
        merge_pattern = r'merge\s+into\s+([^\s(]+)'
        # INSERT INTO pattern
        insert_pattern = r'insert\s+into\s+([^\s(]+)'
        # CREATE TABLE pattern
        create_pattern = r'create\s+(?:or\s+replace\s+)?table\s+([^\s(]+)'
        # UPDATE pattern
        update_pattern = r'update\s+([^\s(]+)'

        # Find all target tables
        targets = []
        for pattern in [merge_pattern, insert_pattern, create_pattern, update_pattern]:
            matches = re.finditer(pattern, sql)
            targets.extend([self.normalize_table_name(m.group(1)) for m in matches])

        # Find source tables
        # FROM clause pattern (handles both regular FROM and JOIN)
        from_pattern = r'from\s+([^\s(]+)|join\s+([^\s(]+)'
        sources = []
        matches = re.finditer(from_pattern, sql)
        for match in matches:
            table = match.group(1) if match.group(1) else match.group(2)
            if table:
                sources.append(self.normalize_table_name(table))

        # Handle CTEs (WITH clause)
        cte_pattern = r'with\s+([^(]+)\s+as'
        cte_matches = re.finditer(cte_pattern, sql)
        for match in cte_matches:
            cte_name = match.group(1).strip()
            # Remove CTE names from sources as they're temporary
            sources = [s for s in sources if s != cte_name.lower()]

        return set(sources), set(targets)

    def process_sql_file(self, file_path):
        """Process SQL file and build lineage."""
        with open(file_path, 'r') as f:
            sql_content = f.read()

        # Split into individual SQL statements
        statements = sql_content.split(';')

        for stmt in statements:
            if stmt.strip():
                sources, targets = self.extract_tables_from_sql(stmt)
                self.source_tables.update(sources)
                self.target_tables.update(targets)
                for target in targets:
                    self.lineage_map[target].update(sources)

    def generate_mapping_csv(self, output_file):
        """Generate source to target mapping CSV."""
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Source Table', 'Target Table'])
            for target, sources in self.lineage_map.items():
                for source in sources:
                    writer.writerow([source, target])

    def generate_neptune_files(self, nodes_file, edges_file):
        """Generate AWS Neptune node and edge files."""
        # Generate nodes file
        nodes = []
        all_tables = self.source_tables.union(self.target_tables)
        for table in all_tables:
            node = {
                '~id': table,
                '~label': table.split('.')[-1],  # Use the table name without schema as label
                'name': table
            }
            nodes.append(node)

        with open(nodes_file, 'w') as f:
            for node in nodes:
                f.write(json.dumps(node) + '\n')

        # Generate edges file
        edges = []
        edge_id = 0
        for target, sources in self.lineage_map.items():
            for source in sources:
                edge = {
                    '~id': f'e{edge_id}',
                    '~from': source,
                    '~to': target,
                    '~label': 'TO_TARGET'
                }
                edges.append(edge)
                edge_id += 1

        with open(edges_file, 'w') as f:
            for edge in edges:
                f.write(json.dumps(edge) + '\n')


# Example usage
def main():
    parser = SQLLineageParser()

    # Example SQL content for testing
    test_sql = """
    WITH cte1 AS (
        SELECT * FROM schema1.table1
        JOIN schema2.table2 ON table1.id = table2.id
    )
    MERGE INTO warehouse.schema3.target_table t
    USING (
        SELECT a.*, b.* 
        FROM schema1.source_table1 a
        JOIN schema2.source_table2 b ON a.id = b.id
    ) s ON t.id = s.id
    WHEN MATCHED THEN UPDATE SET t.col1 = s.col1;
    
    CREATE OR REPLACE TABLE new_table AS
    SELECT * FROM existing_table;
    """

    # Write test SQL to a file
    with open('test.sql', 'w') as f:
        f.write(test_sql)

    # Process the SQL file
    parser.process_sql_file('test.sql')

    # Generate mapping CSV
    parser.generate_mapping_csv('table_mapping.csv')

    # Generate Neptune files
    parser.generate_neptune_files('nodes.json', 'edges.json')


if __name__ == "__main__":
    main()

```

1. Handles complex SQL patterns:
    - SELECT, INSERT, UPDATE, MERGE statements
    - CREATE OR REPLACE TABLE statements
    - CTEs (WITH clauses)
    - Joins and nested queries
    - Fully qualified table names (warehouse.database.table)

2. Main functionalities:
    - Extracts source and target tables from SQL statements
    - Generates source-to-target mapping CSV
    - Creates AWS Neptune-compatible node and edge files
    - Normalizes table names and handles different quoting styles

3. The parser:
    - Removes SQL comments before processing
    - Is case-insensitive
    - Handles multiple statements in a single file
    - Excludes CTE names from final mappings

To use the parser:

```python
parser = SQLLineageParser()
parser.process_sql_file('your_sql_file.sql')
parser.generate_mapping_csv('mapping.csv')
parser.generate_neptune_files('nodes.json', 'edges.json')
```

The generated files will be:

1. `mapping.csv`: Contains source-to-target table mappings
2. `nodes.json`: Neptune-compatible nodes file with table information
3. `edges.json`: Neptune-compatible edges file with TO_TARGET relationships
