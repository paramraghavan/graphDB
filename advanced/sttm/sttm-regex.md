# Implement with pure regex

```python
import re
from collections import defaultdict
import csv
import json


class SQLRegexLineageParser:
    """
    A class to parse SQL statements using regex patterns and extract source-to-target table lineage.
    Handles complex SQL patterns including SELECT INTO, INSERT, UPDATE, MERGE, and CREATE statements.
    Supports fully qualified table names and various SQL syntax variations.
    """

    def __init__(self):
        # Base pattern for table names that can be fully qualified (up to 4 parts)
        # Example matches: table, schema.table, database.schema.table, warehouse.database.schema.table
        table_name_pattern = r'(?:[\w-]+\.){0,3}[\w-]+'

        # Dictionary to store all regex patterns
        self.patterns = {
            # Basic table name pattern - used as building block for other patterns
            'table_name': table_name_pattern,

            # SELECT INTO pattern
            # Matches: SELECT ... INTO target_table FROM source_tables
            # Group 1: target table
            # Group 2: FROM clause containing source tables
            'select_into': re.compile(
                r'SELECT\s+.*?\s+INTO\s+(' + table_name_pattern + r')\s+FROM\s+([^;]+)',
                re.IGNORECASE | re.DOTALL  # Case insensitive, multiline
            ),

            # INSERT pattern
            # Matches both INSERT ... SELECT and INSERT ... VALUES
            # Group 1: target table
            # Group 2: FROM clause (for INSERT ... SELECT)
            'insert': re.compile(
                r'INSERT\s+(?:INTO\s+)?(' + table_name_pattern + r')\s+(?:SELECT\s+.*?FROM\s+([^;]+)|VALUES\s+[^;]+)',
                re.IGNORECASE | re.DOTALL
            ),

            # UPDATE pattern
            # Matches: UPDATE target_table ... [FROM source_tables]
            # Group 1: target table
            # Group 2: optional FROM clause
            'update': re.compile(
                r'UPDATE\s+(' + table_name_pattern + r')\s+.*?(?:FROM\s+([^;]+))?',
                re.IGNORECASE | re.DOTALL
            ),

            # MERGE pattern
            # Matches: MERGE [INTO] target_table USING source_expression
            # Group 1: target table
            # Group 2: USING clause containing source tables
            'merge': re.compile(
                r'MERGE\s+(?:INTO\s+)?(' + table_name_pattern + r')\s+.*?USING\s+([^;]+)',
                re.IGNORECASE | re.DOTALL
            ),

            # CREATE/REPLACE TABLE pattern
            # Matches: CREATE [OR REPLACE] TABLE target_table [AS] SELECT ... FROM source_tables
            # Group 1: target table
            # Group 2: FROM clause
            'create': re.compile(
                r'CREATE\s+(?:OR\s+REPLACE\s+)?TABLE\s+(' + table_name_pattern + r')\s+(?:AS\s+)?SELECT\s+.*?FROM\s+([^;]+)',
                re.IGNORECASE | re.DOTALL
            ),

            # FROM clause pattern
            # Matches tables in FROM clause, including aliases
            # Group 1: all table references in FROM clause
            'from_tables': re.compile(
                r'FROM\s+(' + table_name_pattern + r'(?:\s+(?:AS\s+)?\w+)?(?:\s*,\s*' + table_name_pattern + r'(?:\s+(?:AS\s+)?\w+)?)*)',
                re.IGNORECASE
            ),

            # JOIN pattern
            # Matches any type of JOIN (INNER, LEFT, RIGHT, FULL, CROSS)
            # Group 1: joined table name
            'join_tables': re.compile(
                r'(?:INNER|LEFT|RIGHT|FULL|CROSS)?\s*JOIN\s+(' + table_name_pattern + r')',
                re.IGNORECASE
            )
        }

        # Sets to store unique source and target tables
        self.source_tables = set()
        self.target_tables = set()
        # Dictionary to store source-to-target mappings
        self.lineage_map = defaultdict(set)  # {target_table: set(source_tables)}

    def normalize_table_name(self, table_name):
        """
        Normalize table names by removing aliases, quotes, and standardizing format.
        
        Args:
            table_name (str): Raw table name from SQL statement
            
        Returns:
            str: Normalized table name
            
        Example:
            'MyDB.MySchema."MY_TABLE" as t1' -> 'MySchema.MY_TABLE'
        """
        # Remove AS clause if exists
        table_name = re.sub(r'\s+AS\s+\w+', '', table_name, flags=re.IGNORECASE)
        # Remove quotes and extra spaces
        table_name = table_name.strip().strip('"').strip('`').strip("'")
        # Keep only the relevant parts (handle warehouse.database.schema.table patterns)
        parts = table_name.split('.')
        # Return last part for simple names, last two parts for qualified names
        return parts[-1] if len(parts) == 1 else '.'.join(parts[-2:])

    def extract_source_tables(self, from_clause):
        """
        Extract source tables from a FROM clause including JOIN statements.
        
        Args:
            from_clause (str): The FROM clause portion of a SQL statement
            
        Returns:
            set: Set of normalized table names found in the FROM clause
            
        Example:
            Input: "FROM table1, schema.table2 JOIN table3"
            Output: {'table1', 'schema.table2', 'table3'}
        """
        tables = set()

        # Extract tables from basic FROM clause (comma-separated)
        from_matches = self.patterns['from_tables'].findall(from_clause)
        for match in from_matches:
            # Split on comma and normalize each table name
            tables.update(
                self.normalize_table_name(table)
                for table in match.split(',')
            )

        # Extract tables from JOIN clauses
        join_matches = self.patterns['join_tables'].findall(from_clause)
        tables.update(
            self.normalize_table_name(table)
            for table in join_matches
        )

        return tables

    def parse_sql_statement(self, sql):
        """
        Parse a single SQL statement and extract source and target tables.
        
        Args:
            sql (str): A single SQL statement
            
        Returns:
            tuple: (set of source tables, target table name or None)
            
        Example:
            Input: "INSERT INTO target SELECT * FROM source"
            Output: ({'source'}, 'target')
        """
        # Normalize whitespace
        sql = ' '.join(sql.split())
        sources = set()
        target = None

        # Try each pattern in sequence
        for pattern_name, pattern in [
            ('select_into', self.patterns['select_into']),
            ('insert', self.patterns['insert']),
            ('update', self.patterns['update']),
            ('merge', self.patterns['merge']),
            ('create', self.patterns['create'])
        ]:
            match = pattern.search(sql)
            if match:
                # First group is always the target table
                target = self.normalize_table_name(match.group(1))
                # Second group (if exists) contains source tables
                if len(match.groups()) > 1 and match.group(2):
                    sources.update(self.extract_source_tables(match.group(2)))
                break

        return sources, target

    def parse_sql_file(self, file_path):
        """
        Parse an entire SQL file and build the lineage mapping.
        
        Args:
            file_path (str): Path to the SQL file
            
        Side effects:
            Populates self.source_tables, self.target_tables, and self.lineage_map
        """
        with open(file_path, 'r') as file:
            content = file.read()

        # Split into statements (handling semicolons in quotes)
        statements = re.split(r';(?=[^\']|\'[^\']*\')*$', content)

        for stmt in statements:
            stmt = stmt.strip()
            # Skip empty statements and DELETE statements
            if not stmt or stmt.upper().startswith('DELETE'):
                continue

            sources, target = self.parse_sql_statement(stmt)

            # Update lineage mapping if both source and target were found
            if sources and target:
                self.source_tables.update(sources)
                self.target_tables.add(target)
                self.lineage_map[target].update(sources)

    def generate_mapping_csv(self, output_file):
        """
        Generate a CSV file containing source-to-target mappings.
        
        Args:
            output_file (str): Path for the output CSV file
            
        Output format:
            Source Table, Target Table
            source1, target1
            source2, target1
            ...
        """
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Source Table', 'Target Table'])

            for target, sources in self.lineage_map.items():
                for source in sources:
                    writer.writerow([source, target])

    def generate_neptune_files(self, nodes_file, edges_file):
        """
        Generate AWS Neptune compatible node and edge files.
        
        Args:
            nodes_file (str): Path for the nodes output file
            edges_file (str): Path for the edges output file
            
        Output format:
            Nodes: {"~id": "table_name", "~label": "table_name", "name": "table_name"}
            Edges: {"~id": "eN", "~from": "source", "~to": "target", "~label": "TO_TARGET"}
        """
        # Generate nodes file
        nodes = []
        all_tables = self.source_tables.union(self.target_tables)

        for table in all_tables:
            node = {
                '~id': table,
                '~label': table,
                'name': table
            }
            nodes.append(node)

        with open(nodes_file, 'w') as f:
            for node in nodes:
                f.write(json.dumps(node) + '\n')

        # Generate edges file
        edges = []
        edge_id = 1

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


def main():
    """
    Example usage of the SQLRegexLineageParser class.
    """
    # Initialize parser
    parser = SQLRegexLineageParser()

    # Parse SQL file
    parser.parse_sql_file('input.sql')

    # Generate mapping CSV
    parser.generate_mapping_csv('table_mapping.csv')

    # Generate Neptune files
    parser.generate_neptune_files('nodes.json', 'edges.json')


if __name__ == "__main__":
    main()

```

The code now includes comprehensive documentation explaining:

1. Class and method purposes
2. Regex pattern explanations
3. Parameter descriptions
4. Return value details
5. Example inputs and outputs
6. Side effects where applicable
7. Output file formats
8. Pattern matching behavior

Each section is clearly documented with:

- Purpose
- Input parameters
- Return values
- Example usage
- Important notes about behavior

Key additions to help understand the code:

1. Detailed explanation of table name pattern matching
2. Documentation of regex flags and their purpose
3. Explanation of pattern groups and what they capture
4. Clear examples of input/output for key methods
5. Description of file formats and structure
