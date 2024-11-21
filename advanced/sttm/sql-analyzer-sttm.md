
Analyze SQL statements and generating source-to-target mappings.

```python
import sqlparse
import re
import pandas as pd
import csv
from typing import List, Dict, Set, Tuple


class SQLLineageAnalyzer:
    def __init__(self):
        self.source_tables: Set[str] = set()
        self.target_tables: Set[str] = set()
        self.mappings: List[Dict[str, str]] = []

    def extract_tables(self, sql: str) -> Tuple[Set[str], Set[str]]:
        """
        Extract source and target tables from a SQL statement
        """
        # Normalize SQL statement
        sql = sql.upper()

        # Parse the SQL statement
        parsed = sqlparse.parse(sql)[0]

        sources = set()
        targets = set()

        # Extract target tables
        if sql.startswith('INSERT'):
            # Extract target from INSERT INTO statement
            match = re.search(r'INSERT\s+INTO\s+([^\s\(]+)', sql)
            if match:
                targets.add(match.group(1))

        elif sql.startswith('MERGE'):
            # Extract target from MERGE INTO statement
            match = re.search(r'MERGE\s+INTO\s+([^\s\(]+)', sql)
            if match:
                targets.add(match.group(1))

        elif 'CREATE TABLE' in sql or 'CREATE OR REPLACE TABLE' in sql:
            # Extract target from CREATE TABLE statement
            match = re.search(r'CREATE\s+(?:OR\s+REPLACE\s+)?TABLE\s+([^\s\(]+)', sql)
            if match:
                targets.add(match.group(1))

        # Extract source tables
        # Look for tables after FROM and JOIN clauses
        from_pattern = r'FROM\s+([^\s\(\)]+)'
        join_pattern = r'JOIN\s+([^\s\(\)]+)'

        sources.update(re.findall(from_pattern, sql))
        sources.update(re.findall(join_pattern, sql))

        # Remove any schema prefixes
        sources = {table.split('.')[-1] for table in sources}
        targets = {table.split('.')[-1] for table in targets}

        # Remove targets from sources if they appear there
        sources = sources - targets

        return sources, targets

    def analyze_sql_file(self, file_path: str):
        """
        Analyze a file containing SQL statements and build source-to-target mappings
        """
        with open(file_path, 'r') as f:
            sql_content = f.read()

        # Split into individual statements
        statements = sqlparse.split(sql_content)

        for stmt in statements:
            # Skip empty statements and DELETE statements
            if not stmt.strip() or stmt.upper().startswith('DELETE'):
                continue

            sources, targets = self.extract_tables(stmt)

            # Update overall sets
            self.source_tables.update(sources)
            self.target_tables.update(targets)

            # Create mappings
            for target in targets:
                for source in sources:
                    self.mappings.append({
                        'source': source,
                        'target': target
                    })

    def generate_csv_mapping(self, output_file: str):
        """
        Generate CSV file with source-to-target mappings
        """
        df = pd.DataFrame(self.mappings)
        df.drop_duplicates().to_csv(output_file, index=False)

    def generate_neptune_files(self, nodes_file: str, edges_file: str):
        """
        Generate Neptune-compatible nodes and edges files
        """
        # Generate nodes file
        all_tables = list(self.source_tables.union(self.target_tables))
        nodes = [{'~id': table, '~label': table} for table in all_tables]

        with open(nodes_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['~id', '~label'])
            writer.writeheader()
            writer.writerows(nodes)

        # Generate edges file
        edges = []
        for mapping in self.mappings:
            edge = {
                '~id': f"{mapping['source']}_to_{mapping['target']}",
                '~from': mapping['source'],
                '~to': mapping['target'],
                '~label': 'to_target'
            }
            edges.append(edge)

        with open(edges_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['~id', '~from', '~to', '~label'])
            writer.writeheader()
            writer.writerows(edges)


# Example usage
def analyze_sql_lineage(sql_file_path: str):
    analyzer = SQLLineageAnalyzer()

    # Analyze SQL file
    analyzer.analyze_sql_file(sql_file_path)

    # Generate CSV mapping
    analyzer.generate_csv_mapping('table_mappings.csv')

    # Generate Neptune files
    analyzer.generate_neptune_files('nodes.csv', 'edges.csv')

    return {
        'source_tables': list(analyzer.source_tables),
        'target_tables': list(analyzer.target_tables),
        'total_mappings': len(analyzer.mappings)
    }

```


1. The `SQLLineageAnalyzer` class:
    - Parses SQL statements using `sqlparse`
    - Extracts source and target tables using regex patterns
    - Handles various SQL operations (SELECT, INSERT, MERGE, CREATE TABLE)
    - Generates both CSV mappings and Neptune-compatible files

2. Main features:
    - Skips DELETE statements as requested
    - Handles complex SQL with joins and nested queries
    - Removes schema prefixes from table names
    - Generates deduplicated mappings
    - Creates Neptune-compatible nodes and edges files

3. To use it:

```python
# Example usage
result = analyze_sql_lineage('your_sql_file.sql')
print(result)
```

This will generate three files:

- `table_mappings.csv`: Source-to-target mappings
- `nodes.csv`: Neptune nodes file with table names as labels
- `edges.csv`: Neptune edges file with "to_target" relationships

The script requires these Python packages:

```bash
pip install sqlparse pandas
```

Limitations to be aware of:

1. The regex patterns might need adjustment for very complex SQL
2. It might not catch all edge cases in highly nested queries
3. CTEs (Common Table Expressions) might need additional handling
4. Some complex Snowflake-specific syntax might need additional patterns
