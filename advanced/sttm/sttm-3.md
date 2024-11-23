Create a Python solution to analyze SQL statements and generate source-to-target mappings along with
Neptune graph files.

```python
import sqlparse
import re
import csv
import pandas as pd
from typing import Dict, Set, List, Tuple


class SQLLineageAnalyzer:
    def __init__(self):
        self.source_tables: Set[str] = set()
        self.target_tables: Set[str] = set()
        self.mappings: List[Dict[str, str]] = []

    def clean_table_name(self, table_name: str) -> str:
        """Clean table names by removing schema, quotes, etc."""
        # Remove schema prefixes if present
        if '.' in table_name:
            table_name = table_name.split('.')[-1]
        # Remove quotes and whitespace
        return re.sub(r'["\'\[\]]', '', table_name.strip())

    def extract_tables_from_sql(self, sql: str) -> Tuple[Set[str], Set[str]]:
        """Extract source and target tables from a SQL statement."""
        sql = sqlparse.format(sql, strip_comments=True)
        parsed = sqlparse.parse(sql)[0]

        # Initialize source and target tables for this statement
        sources = set()
        targets = set()

        # Convert to uppercase for consistent matching
        sql_upper = sql.upper()

        # Identify statement type
        if sql_upper.startswith('SELECT'):
            # Handle SELECT INTO statements
            into_match = re.search(r'INTO\s+(\w+\.?\w+)', sql_upper)
            if into_match:
                targets.add(self.clean_table_name(into_match.group(1)))

            # Extract source tables from FROM and JOIN clauses
            from_match = re.findall(r'FROM\s+(\w+\.?\w+)', sql_upper)
            join_match = re.findall(r'JOIN\s+(\w+\.?\w+)', sql_upper)

            sources.update([self.clean_table_name(t) for t in from_match + join_match])

        elif sql_upper.startswith('INSERT'):
            # Extract target table
            insert_match = re.search(r'INTO\s+(\w+\.?\w+)', sql_upper)
            if insert_match:
                targets.add(self.clean_table_name(insert_match.group(1)))

            # Extract source tables from SELECT part
            from_match = re.findall(r'FROM\s+(\w+\.?\w+)', sql_upper)
            join_match = re.findall(r'JOIN\s+(\w+\.?\w+)', sql_upper)
            sources.update([self.clean_table_name(t) for t in from_match + join_match])

        elif sql_upper.startswith('MERGE'):
            # Extract target table
            merge_match = re.search(r'INTO\s+(\w+\.?\w+)', sql_upper)
            if merge_match:
                targets.add(self.clean_table_name(merge_match.group(1)))

            # Extract source tables
            using_match = re.search(r'USING\s+(\w+\.?\w+)', sql_upper)
            if using_match:
                sources.add(self.clean_table_name(using_match.group(1)))

        elif sql_upper.startswith('CREATE') or sql_upper.startswith('REPLACE'):
            # Extract target table
            create_match = re.search(r'TABLE\s+(\w+\.?\w+)', sql_upper)
            if create_match:
                targets.add(self.clean_table_name(create_match.group(1)))

            # Extract source tables from SELECT part if present
            from_match = re.findall(r'FROM\s+(\w+\.?\w+)', sql_upper)
            join_match = re.findall(r'JOIN\s+(\w+\.?\w+)', sql_upper)
            sources.update([self.clean_table_name(t) for t in from_match + join_match])

        return sources, targets

    def analyze_sql_file(self, file_path: str):
        """Analyze SQL file and build source-to-target mappings."""
        with open(file_path, 'r') as f:
            sql_content = f.read()

        # Split into individual statements
        statements = sqlparse.split(sql_content)

        for stmt in statements:
            if stmt.strip():
                sources, targets = self.extract_tables_from_sql(stmt)

                # Update overall sets
                self.source_tables.update(sources)
                self.target_tables.update(targets)

                # Create mappings
                for source in sources:
                    for target in targets:
                        self.mappings.append({
                            'source': source,
                            'target': target
                        })

    def generate_mapping_csv(self, output_file: str):
        """Generate CSV file with source-to-target mappings."""
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['source', 'target'])
            writer.writeheader()
            writer.writerows(self.mappings)

    def generate_neptune_files(self, nodes_file: str, edges_file: str):
        """Generate Neptune-compatible CSV files for nodes and edges."""
        # Generate nodes file
        all_tables = self.source_tables.union(self.target_tables)
        nodes_df = pd.DataFrame({
            '~id': list(all_tables),
            '~label': ['Table'] * len(all_tables),
            'name': list(all_tables)
        })
        nodes_df.to_csv(nodes_file, index=False)

        # Generate edges file
        edges_df = pd.DataFrame(self.mappings)
        edges_df['~id'] = [f"e{i}" for i in range(len(edges_df))]
        edges_df['~label'] = ['TO_TARGET'] * len(edges_df)
        edges_df['~from'] = edges_df['source']
        edges_df['~to'] = edges_df['target']
        edges_df = edges_df[['~id', '~label', '~from', '~to']]
        edges_df.to_csv(edges_file, index=False)


def main():
    # Example usage
    analyzer = SQLLineageAnalyzer()
    analyzer.analyze_sql_file('input.sql')

    # Generate mapping CSV
    analyzer.generate_mapping_csv('table_mappings.csv')

    # Generate Neptune files
    analyzer.generate_neptune_files('nodes.csv', 'edges.csv')


if __name__ == "__main__":
    main()

```

I've created a Python script that can analyze SQL statements and generate source-to-target mappings along with Neptune
graph files. Here are the key features:

1. SQL Statement Analysis:
    - Handles SELECT, INSERT, MERGE, CREATE/REPLACE statements
    - Extracts tables from FROM, JOIN, INTO, and USING clauses
    - Handles schema-qualified names and quoted identifiers
    - Ignores DELETE statements as requested

2. Source-to-Target Mapping:
    - Generates a CSV file with source and target table mappings
    - Handles complex cases like multiple source tables joining to one target
    - Cleans table names by removing schemas and quotes

3. Neptune Graph Generation:
    - Creates nodes.csv with table names as nodes
    - Creates edges.csv with TO_TARGET relationships
    - Follows Neptune's CSV format requirements with ~id, ~label, ~from, ~to

To use the script:

```python
analyzer = SQLLineageAnalyzer()
analyzer.analyze_sql_file('your_sql_file.sql')
analyzer.generate_mapping_csv('mappings.csv')
analyzer.generate_neptune_files('nodes.csv', 'edges.csv')
```

The script uses these libraries:

- sqlparse: For SQL parsing and statement splitting
- pandas: For CSV generation
- re: For regular expression pattern matching

Some limitations to be aware of:

1. The parser might miss tables in very complex subqueries
2. It assumes well-formatted SQL
3. CTEs (Common Table Expressions) might need additional handling
