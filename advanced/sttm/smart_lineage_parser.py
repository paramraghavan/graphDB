import sqlparse
import re
from collections import defaultdict
import csv
import json
import datetime
import os


def extract_sql_statements(log_file_path, output_file=None):
    """
    Extract SQL statements from a log file.

    Args:
        log_file_path (str): Path to the log file
        output_file (str, optional): Path to save extracted SQL statements.
                                   If None, prints to console.

    Returns:
        list: List of dictionaries containing SQL statements and metadata
    """
    # Common SQL keywords to help identify SQL statements
    sql_keywords = r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|CREATE OR REPLACE|DROP|ALTER|MERGE|TRUNCATE|BEGIN|COMMIT|ROLLBACK)\b'

    # Regular expression pattern to match SQL statements
    # This pattern looks for SQL keywords followed by text until a semicolon or new line
    sql_pattern = f"({sql_keywords}.*?)(;|\n)"

    # Store extracted statements with metadata
    extracted_statements = []

    try:
        with open(log_file_path, 'r', encoding='utf-8') as file:
            content = file.read()

            # Find all matches in the content
            matches = re.finditer(sql_pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)

            for match in matches:
                sql_statement = match.group(1).strip()

                # Skip if the statement is too short (likely a false positive)
                if len(sql_statement) < 10:
                    continue

                # Try to extract timestamp if it exists in the line
                timestamp_match = re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',
                                            match.string[:match.start()])
                timestamp = timestamp_match.group(0) if timestamp_match else None

                statement_info = {
                    'timestamp': timestamp,
                    'statement': sql_statement,
                    'type': re.match(sql_keywords, sql_statement, re.IGNORECASE).group(0).upper()
                }

                extracted_statements.append(statement_info)

        return extracted_statements

    except FileNotFoundError:
        print(f"Error: File {log_file_path} not found")
        return []
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return []


class SQLLineageParser:
    def __init__(self):
        """Initialize the parser with data structures to store mappings"""
        self.source_tables = set()
        self.target_tables = set()
        self.mappings = []
        self.last_target = None
        self.table_aliases = {}  # Store table aliases for better join handling

    def clean_table_name(self, table_name):
        """Clean table name by removing aliases and quotes"""
        table_name = table_name.strip()
        # Remove quotes if present
        if table_name.startswith('"') and table_name.endswith('"'):
            table_name = table_name[1:-1]
        # Handle alias removal
        parts = table_name.split(' AS ')
        if len(parts) > 1:
            table_name = parts[0].strip()
        return table_name.strip()

    def extract_aliases(self, sql):
        """Extract table aliases from SQL statement"""
        # Reset aliases for new statement
        self.table_aliases = {}

        # Pattern to match table names with aliases
        alias_pattern = r'(\b\w+(?:\.\w+)*\b)(?:\s+(?:AS\s+)?(\w+))?(?=\s*(?:,|\s+(?:JOIN|ON|WHERE|GROUP|ORDER|HAVING|WINDOW|LIMIT|$)))'

        matches = re.finditer(alias_pattern, sql, re.IGNORECASE)
        for match in matches:
            table_name = match.group(1)
            alias = match.group(2)
            if alias:
                self.table_aliases[alias.upper()] = table_name.upper()

    def extract_table_names(self, sql_info):
        """
        Extract table names from SQL statement with enhanced CREATE OR REPLACE handling.

        Args:
            sql_info (dict): Dictionary containing SQL statement and metadata
        Returns:
            tuple: Lists of source and target tables found in the statement
        """
        sql = sql_info['statement']
        sql_type = sql_info['type']

        # Normalize SQL statement
        sql = ' '.join(sql.split()).upper()

        # Extract aliases first
        self.extract_aliases(sql)

        sources = set()
        targets = set()

        # Enhanced pattern for table names including warehouse.database.table format
        table_pattern = r'(?:[\w]+\.){0,3}[\w]+(?=\s|$|\))'

        # Special handling for CREATE OR REPLACE TABLE AS SELECT
        create_replace_match = re.search(
            r'CREATE\s+(?:OR\s+REPLACE\s+)?TABLE\s+([\w\.]+)(?:\s+AS\s+)?',
            sql,
            re.IGNORECASE
        )

        if create_replace_match:
            target_table = self.clean_table_name(create_replace_match.group(1))
            targets.add(target_table)
            self.last_target = target_table

            # Extract source tables after the SELECT
            select_pos = sql.find('SELECT')
            if select_pos != -1:
                select_part = sql[select_pos:]

                # Find tables in FROM clause
                from_matches = re.finditer(
                    r'FROM\s+({})\s*(?:AS\s+\w+)?'.format(table_pattern),
                    select_part
                )
                for match in from_matches:
                    table_name = self.clean_table_name(match.group(1))
                    sources.add(table_name)

                # Find tables in JOIN clauses
                join_matches = re.finditer(
                    r'JOIN\s+({})\s*(?:AS\s+\w+)?'.format(table_pattern),
                    select_part
                )
                for match in join_matches:
                    table_name = self.clean_table_name(match.group(1))
                    sources.add(table_name)

        # Handle regular INSERT/UPDATE/MERGE statements
        elif sql_type in ('INSERT', 'UPDATE', 'MERGE'):
            if 'VALUES' in sql:
                target_match = re.search(f"INTO\s+({table_pattern})", sql)
                if target_match:
                    target_table = self.clean_table_name(target_match.group(1))
                    targets.add(target_table)
                    sources.add(target_table)  # Use target as source for VALUES
                    self.last_target = target_table
            else:
                # Extract target table
                target_match = re.search(
                    f"(?:INTO|UPDATE|MERGE INTO)\s+({table_pattern})",
                    sql
                )
                if target_match:
                    target_table = self.clean_table_name(target_match.group(1))
                    targets.add(target_table)
                    self.last_target = target_table

                # Extract source tables
                from_matches = re.finditer(
                    r'FROM\s+({})\s*(?:AS\s+\w+)?'.format(table_pattern),
                    sql
                )
                for match in from_matches:
                    table_name = self.clean_table_name(match.group(1))
                    sources.add(table_name)

                join_matches = re.finditer(
                    r'JOIN\s+({})\s*(?:AS\s+\w+)?'.format(table_pattern),
                    sql
                )
                for match in join_matches:
                    table_name = self.clean_table_name(match.group(1))
                    sources.add(table_name)

        # Resolve aliases in sources
        resolved_sources = set()
        for source in sources:
            if source in self.table_aliases:
                resolved_sources.add(self.table_aliases[source])
            else:
                resolved_sources.add(source)

        # Remove CTE names
        cte_pattern = r'WITH\s+(\w+)\s+AS\s*\('
        cte_names = set(re.findall(cte_pattern, sql))
        resolved_sources = {table for table in resolved_sources if table not in cte_names}

        return list(resolved_sources), list(targets)

    def process_sql_file(self, file_path):
        """
        Process SQL file and extract source-to-target mappings

        Args:
            file_path (str): Path to SQL file
        """
        statements = extract_sql_statements(file_path, None)

        for stmt in statements:
            if stmt['statement'].strip():
                sources, targets = self.extract_table_names(stmt)

                # Store all unique tables
                self.source_tables.update(sources)
                self.target_tables.update(targets)

                # Create mappings for each source-target pair
                for target in targets:
                    for source in sources:
                        self.mappings.append({
                            'source': source,
                            'target': target,
                            'timestamp': stmt['timestamp'],
                            'type': stmt['type']
                        })

    def generate_mapping_csv(self, output_file):
        """
        Generate CSV file with source-to-target mappings

        Args:
            output_file (str): Output CSV file path
        """
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['source', 'target', 'timestamp', 'type'])
            writer.writeheader()
            writer.writerows(self.mappings)

    def generate_neptune_files(self, nodes_file, edges_file):
        """
        Generate node and edge files for AWS Neptune

        Args:
            nodes_file (str): Output file path for nodes
            edges_file (str): Output file path for edges
        """
        # Generate nodes file
        nodes = []
        all_tables = self.source_tables.union(self.target_tables)

        for table in all_tables:
            nodes.append({
                '~id': table,
                '~label': table.split('.')[-1],
                'name': table
            })

        # Generate edges file
        edges = []
        for idx, mapping in enumerate(self.mappings):
            edges.append({
                '~id': f'e{idx}',
                '~from': mapping['source'],
                '~to': mapping['target'],
                '~label': 'TO_TARGET',
                'timestamp': mapping['timestamp'],
                'type': mapping['type']
            })

        # Write nodes file
        with open(nodes_file, 'w') as f:
            for node in nodes:
                f.write(json.dumps(node) + '\n')

        # Write edges file
        with open(edges_file, 'w') as f:
            for edge in edges:
                f.write(json.dumps(edge) + '\n')