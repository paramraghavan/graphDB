import sqlparse
import re
from collections import defaultdict
import csv
import json
import datetime
import os
from datetime import datetime

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

        # Write to output file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"SQL Statements Extracted from {os.path.basename(log_file_path)}\n")
                f.write(f"Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                for stmt in extracted_statements:
                    f.write("-" * 80 + "\n")
                    if stmt['timestamp']:
                        f.write(f"Timestamp: {stmt['timestamp']}\n")
                    f.write(f"Type: {stmt['type']}\n")
                    f.write("Statement:\n")
                    f.write(f"{stmt['statement']}\n\n")

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
        self.table_relationships = defaultdict(set)  # Store relationships between tables
        self.mappings = []

    def extract_table_names(self, sql):
        """
        Extract table names from SQL statement considering various formats:
        - database.table
        - warehouse.database.table
        - database.schema.table

        Args:
            sql (str): SQL statement to parse
        Returns:
            tuple: Lists of source and target tables found in the statement
        """
        # Normalize SQL statement
        sql = ' '.join(sql.split()).upper()

        # Patterns for different table name formats
        table_pattern = r'(?:[\w]+\.){0,3}[\w]+(?=\s|$|\))'

        sources = set()
        targets = set()

        # Parse the SQL statement
        try:
            parsed = sqlparse.parse(sql)[0]
        except IndexError:
            return [], []  # Return empty lists if parsing fails

        # Determine statement type
        stmt_type = parsed.get_type()

        if stmt_type == 'DELETE':
            return [], []  # Skip DELETE statements as requested

        # Extract target tables based on statement type
        if stmt_type in ('INSERT', 'UPDATE', 'MERGE'):
            # Find target table after INSERT INTO, UPDATE, or MERGE INTO
            target_match = re.search(f"(?:INTO|UPDATE|MERGE INTO)\s+({table_pattern})", sql)
            if target_match:
                targets.add(target_match.group(1))

        elif 'CREATE' in sql or 'REPLACE' in sql:
            # Find target table after CREATE TABLE or CREATE OR REPLACE TABLE
            target_match = re.search(f"(?:CREATE|REPLACE)\s+TABLE\s+({table_pattern})", sql)
            if target_match:
                targets.add(target_match.group(1))

        # Extract source tables from FROM and JOIN clauses more comprehensively
        # Handle basic FROM clause
        from_match = re.search(r'FROM\s+({})'.format(table_pattern), sql)
        if from_match:
            sources.add(from_match.group(1))

        # Handle all types of JOINs
        join_pattern = r'(?:LEFT|RIGHT|INNER|OUTER|CROSS|FULL)?\s*JOIN\s+({})'.format(table_pattern)
        join_matches = re.finditer(join_pattern, sql)
        for match in join_matches:
            sources.add(match.group(1))

        # Handle subqueries in FROM clause
        subquery_pattern = r'FROM\s+\((.*?)\)\s+(?:AS\s+)?(\w+)'
        subqueries = re.finditer(subquery_pattern, sql, re.DOTALL)
        for subquery in subqueries:
            subquery_sources, _ = self.extract_table_names(subquery.group(1))
            sources.update(subquery_sources)

        # Handle CTEs (Common Table Expressions)
        cte_pattern = r'WITH\s+(\w+)\s+AS\s*\('
        cte_names = set(re.findall(cte_pattern, sql))

        # Remove CTE names from sources as they're temporary
        sources = {table for table in sources if table not in cte_names}

        return list(sources), list(targets)

    def process_sql_file(self, file_path):
        """
        Process SQL file and extract source-to-target mappings

        Args:
            file_path (str): Path to SQL file
        """
        statements = extract_sql_statements(file_path, None)
        for stmt_info in statements:
            stmt = stmt_info['statement']
            if stmt.strip():
                sources, targets = self.extract_table_names(stmt)

                # Store all unique tables
                self.source_tables.update(sources)
                self.target_tables.update(targets)

                # Store relationships between tables
                for target in targets:
                    self.table_relationships[target].update(sources)
                    # Create mappings for the current statement
                    self.mappings.append({
                        'target': target,
                        'sources': list(sources),
                        'timestamp': stmt_info.get('timestamp'),
                        'statement_type': stmt_info.get('type')
                    })

    def generate_mapping_csv(self, output_file):
        """
        Generate CSV file with source-to-target mappings

        Args:
            output_file (str): Output CSV file path
        """
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['target', 'sources', 'timestamp', 'statement_type'])
            for mapping in self.mappings:
                writer.writerow([
                    mapping['target'],
                    '|'.join(mapping['sources']),  # Join multiple sources with pipe
                    mapping.get('timestamp', ''),
                    mapping.get('statement_type', '')
                ])

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
                '~label': table.split('.')[-1],  # Use last part of table name as label
                'name': table,
                'type': 'TARGET' if table in self.target_tables else 'SOURCE'
            })

        # Generate edges file with relationship metadata
        edges = []
        edge_id = 0
        for mapping in self.mappings:
            target = mapping['target']
            for source in mapping['sources']:
                edges.append({
                    '~id': f'e{edge_id}',
                    '~from': source,
                    '~to': target,
                    '~label': 'FLOWS_TO',
                    'statement_type': mapping.get('statement_type', ''),
                    'timestamp': mapping.get('timestamp', '')
                })
                edge_id += 1

        # Write nodes file
        with open(nodes_file, 'w') as f:
            for node in nodes:
                f.write(json.dumps(node) + '\n')

        # Write edges file
        with open(edges_file, 'w') as f:
            for edge in edges:
                f.write(json.dumps(edge) + '\n')


def main():
    """
    Main function to demonstrate usage
    """
    # Initialize parser
    parser = SQLLineageParser()

    # Process SQL file
    parser.process_sql_file('input.sql')

    # Generate mapping CSV
    parser.generate_mapping_csv('mappings.csv')

    # Generate Neptune files
    parser.generate_neptune_files('nodes.csv', 'edges.csv')


if __name__ == "__main__":
    main()