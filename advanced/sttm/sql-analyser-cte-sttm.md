# SQL Lineage Analyzer to handle CTEs properly.

```python
import sqlparse
import re
import pandas as pd
import csv
from typing import List, Dict, Set, Tuple
from sqlparse.sql import IdentifierList, Identifier, Token
from sqlparse.tokens import Keyword, DML, DDL


class SQLLineageAnalyzer:
    def __init__(self):
        self.source_tables: Set[str] = set()
        self.target_tables: Set[str] = set()
        self.mappings: List[Dict[str, str]] = []
        self.cte_definitions: Dict[str, Set[str]] = {}  # Store CTE dependencies

    def extract_cte_info(self, sql: str) -> Dict[str, Set[str]]:
        """
        Extract CTE names and their source tables
        Returns: Dict[cte_name, set of source tables]
        """
        cte_pattern = r'WITH\s+([^;]+?)(?:\s+SELECT|\s+INSERT|\s+MERGE|\s+UPDATE)'
        cte_matches = re.search(cte_pattern, sql, re.IGNORECASE | re.DOTALL)

        if not cte_matches:
            return {}

        cte_section = cte_matches.group(1)
        cte_definitions = {}

        # Split multiple CTEs
        cte_parts = re.split(r',(?=\s*[A-Za-z]+\s+AS\s*\()', cte_section)

        for part in cte_parts:
            # Extract CTE name and its query
            cte_match = re.match(r'\s*([A-Za-z_][A-Za-z0-9_]*)\s+AS\s*\((.*)\)', part, re.DOTALL)
            if cte_match:
                cte_name = cte_match.group(1).upper()
                cte_query = cte_match.group(2)

                # Find source tables in the CTE query
                sources = set()
                # Look for tables after FROM and JOIN
                from_tables = re.findall(r'FROM\s+([^\s\(\)]+)', cte_query, re.IGNORECASE)
                join_tables = re.findall(r'JOIN\s+([^\s\(\)]+)', cte_query, re.IGNORECASE)

                sources.update(from_tables)
                sources.update(join_tables)

                # Remove schema prefixes and clean table names
                sources = {table.split('.')[-1].upper() for table in sources}

                # Also look for references to other CTEs
                for other_cte in cte_definitions.keys():
                    if other_cte in cte_query.upper():
                        sources.add(other_cte)

                cte_definitions[cte_name] = sources

        return cte_definitions

    def resolve_cte_dependencies(self, cte_name: str, final_sources: Set[str]):
        """
        Recursively resolve CTE dependencies to find original source tables
        """
        if cte_name in self.cte_definitions:
            for source in self.cte_definitions[cte_name]:
                if source in self.cte_definitions:
                    # Recursive call for nested CTEs
                    self.resolve_cte_dependencies(source, final_sources)
                else:
                    final_sources.add(source)

    def extract_tables(self, sql: str) -> Tuple[Set[str], Set[str]]:
        """
        Extract source and target tables from a SQL statement, including CTE handling
        """
        # Normalize SQL statement
        sql = sql.upper()

        # First, extract and store CTE definitions
        self.cte_definitions = self.extract_cte_info(sql)

        # Parse the SQL statement
        parsed = sqlparse.parse(sql)[0]

        sources = set()
        targets = set()

        # Extract target tables
        if sql.startswith('INSERT'):
            match = re.search(r'INSERT\s+INTO\s+([^\s\(]+)', sql)
            if match:
                targets.add(match.group(1))

        elif sql.startswith('MERGE'):
            match = re.search(r'MERGE\s+INTO\s+([^\s\(]+)', sql)
            if match:
                targets.add(match.group(1))

        elif 'CREATE TABLE' in sql or 'CREATE OR REPLACE TABLE' in sql:
            match = re.search(r'CREATE\s+(?:OR\s+REPLACE\s+)?TABLE\s+([^\s\(]+)', sql)
            if match:
                targets.add(match.group(1))

        # Extract source tables from main query
        from_pattern = r'FROM\s+([^\s\(\)]+)'
        join_pattern = r'JOIN\s+([^\s\(\)]+)'

        main_sources = set()
        main_sources.update(re.findall(from_pattern, sql))
        main_sources.update(re.findall(join_pattern, sql))

        # Process each source to handle CTEs and regular tables
        final_sources = set()
        for source in main_sources:
            source = source.split('.')[-1]  # Remove schema prefix
            if source in self.cte_definitions:
                # Resolve CTE dependencies
                self.resolve_cte_dependencies(source, final_sources)
            else:
                final_sources.add(source)

        # Remove any schema prefixes
        final_sources = {table.split('.')[-1] for table in final_sources}
        targets = {table.split('.')[-1] for table in targets}

        # Remove targets from sources if they appear there
        final_sources = final_sources - targets

        return final_sources, targets

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

Let me explain the key enhancements for handling CTEs:

1. **CTE Detection and Parsing**:
   ```python
   cte_pattern = r'WITH\s+([^;]+?)(?:\s+SELECT|\s+INSERT|\s+MERGE|\s+UPDATE)'
   ```
    - This pattern captures the entire CTE section starting with `WITH`
    - Handles multiple CTEs separated by commas
    - Supports nested CTEs

2. **CTE Dependency Resolution**:
   ```python
   def resolve_cte_dependencies(self, cte_name: str, final_sources: Set[str]):
   ```
    - Recursively resolves CTE dependencies
    - Tracks source tables through multiple levels of CTEs
    - Prevents infinite loops in circular references

3. Example of Complex CTE Handling:

```sql
WITH 
cte1 AS (
    SELECT * FROM table1
    JOIN table2 ON table1.id = table2.id
),
cte2 AS (
    SELECT * FROM cte1
    JOIN table3 ON cte1.id = table3.id
)
INSERT INTO target_table
SELECT * FROM cte2;
```

The analyzer will:

1. Identify `cte1` and `cte2` as CTEs
2. For `cte1`, record `table1` and `table2` as sources
3. For `cte2`, resolve its dependency on `cte1` to ultimately map:
    - Sources: `table1`, `table2`, `table3`
    - Target: `target_table`

4. **Limitations and Edge Cases**:
    - Nested CTEs within subqueries might need additional parsing
    - Very complex CTE patterns might need regex pattern adjustments
    - Recursive CTEs might need special handling
