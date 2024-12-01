import sqlparse
import re
from collections import defaultdict
import csv
import json


class SQLLineageParser:
    def __init__(self):
        """Initialize the parser with data structures to store mappings"""
        self.source_tables = set()
        self.target_tables = set()
        self.mappings = []

        # Common log patterns to clean up
        self.log_patterns = [
            r'^Created\s+\S+\s+\S+\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}:\d{6}.*?(?=SELECT|INSERT|UPDATE|CREATE|MERGE)'
            r'^Populated\s+\S+\s+\S+\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}:\d{6}.*?(?=SELECT|INSERT|UPDATE|CREATE|MERGE)'
            r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}.*?(?=SELECT|INSERT|UPDATE|CREATE|MERGE)',  # Timestamp logs
            r'Running query:.*?(?=SELECT|INSERT|UPDATE|CREATE|MERGE)',  # Query execution logs
            r'INFO:.*?(?=SELECT|INSERT|UPDATE|CREATE|MERGE)',  # Info logs
            r'DEBUG:.*?(?=SELECT|INSERT|UPDATE|CREATE|MERGE)',  # Debug logs
            r'Query completed.*$',  # Query completion logs
            r'Affected rows:.*$',  # Row count logs
            r'Execution time:.*$'  # Execution time logs
        ]

    def clean_sql_statement(self, sql):
        """
        Clean SQL statement by removing log messages and other non-SQL text

        Args:
            sql (str): Raw SQL statement with potential logs
        Returns:
            str: Cleaned SQL statement
        """
        # Remove common log patterns
        cleaned_sql = sql.strip()
        for pattern in self.log_patterns:
            cleaned_sql = re.sub(pattern, '', cleaned_sql, flags=re.IGNORECASE | re.MULTILINE)

        # Remove any remaining lines that don't look like SQL
        sql_lines = []
        for line in cleaned_sql.split(';'): #cleaned_sql.split('\n'):
            line = line.strip()
            # Keep lines that start with common SQL keywords or are part of SQL statements
            if (re.match(
                    r'^(SELECT|INSERT|UPDATE|CREATE|MERGE|FROM|JOIN|WHERE|GROUP|ORDER|HAVING|WITH|AND|OR|UNION|INTO|AS|\()',
                    line, re.IGNORECASE) or
                    re.match(r'^\s*[A-Za-z0-9_\.\(\)]', line)):
                sql_lines.append(line)

        return ' '.join(sql_lines)

    def check_keywords(self, string, keywords):
        for keyword in keywords:
            if keyword in string:
                return True
        return False

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
        # Clean the SQL statement first
        sql = self.clean_sql_statement(sql)

        # Normalize SQL statement
        sql = ' '.join(sql.split()).upper()

        # Enhanced pattern for table names with optional schema/database prefixes
        table_pattern = r'(?:[\w]+\.){0,3}[\w]+(?=\s|$|\))'

        # Pattern to exclude common SQL functions that might be mistaken for table names
        function_pattern = r'\b(COUNT|SUM|AVG|MAX|MIN|COALESCE|CASE|WHEN|THEN|END|AND|OR|IN|EXISTS|BETWEEN)\b'

        sources = set()
        targets = set()

        try:
            # Parse the SQL statement
            parsed = sqlparse.parse(sql)[0]
            stmt_type = parsed.get_type()

            if stmt_type == 'DELETE':
                return [], []

            # Extract target tables
            # if stmt_type in ('INSERT', 'UPDATE', 'MERGE'):
            if self.check_keywords(sql, ['INSERT', 'UPDATE', 'MERGE']):
                target_match = re.search(f"(?:INTO|UPDATE|MERGE INTO)\s+({table_pattern})", sql)
                if target_match and not re.match(function_pattern, target_match.group(1)):
                    targets.add(target_match.group(1))

            elif self.check_keywords(sql, ['CREATE', 'REPLACE']): #'CREATE' in sql or 'REPLACE' in sql:
                target_match = re.search(f"(?:CREATE|REPLACE)\s+(VIEW|TABLE)\s+((?:[\w]+\.){0,3}[\w]+)", sql) #((?:[\w]+\.){0,3}[\w]+)
                if target_match and not re.match(function_pattern, target_match.group(1)):
                    targets.add(target_match.group(1))

            # Extract source tables
            from_clauses = re.finditer(r'FROM\s+({})'.format(table_pattern), sql)
            join_clauses = re.finditer(r'JOIN\s+({})'.format(table_pattern), sql)

            for match in from_clauses:
                table_name = match.group(1)
                if not re.match(function_pattern, table_name):
                    sources.add(table_name)

            for match in join_clauses:
                table_name = match.group(1)
                if not re.match(function_pattern, table_name):
                    sources.add(table_name)

            # Handle CTEs
            cte_pattern = r'WITH\s+(\w+)\s+AS\s*\('
            cte_names = set(re.findall(cte_pattern, sql))
            sources = {table for table in sources if table not in cte_names}

        except Exception as e:
            print(f"Error parsing SQL statement: {e}")
            return [], []

        return list(sources), list(targets)

    def process_sql_file(self, file_path):
        """
        Process SQL file and extract source-to-target mappings

        Args:
            file_path (str): Path to SQL file
        """
        with open(file_path, 'r') as f:
            sql_content = f.read()

        # Split content into SQL statements
        # Look for statement terminators and common log patterns
        statement_pattern = r';|\n\n(?=(?:SELECT|INSERT|UPDATE|CREATE|MERGE))'
        statements = re.split(statement_pattern, sql_content)

        for stmt in statements:
            if stmt.strip():
                sources, targets = self.extract_table_names(stmt)

                # Store unique tables
                self.source_tables.update(sources)
                self.target_tables.update(targets)

                # Create mappings
                for target in targets:
                    for source in sources:
                        self.mappings.append({
                            'source': source,
                            'target': target
                        })

    def generate_mapping_csv(self, output_file):
        """Generate CSV file with source-to-target mappings"""
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['source', 'target'])
            writer.writeheader()
            writer.writerows(self.mappings)

    def generate_neptune_files(self, nodes_file, edges_file):
        """Generate node and edge files for AWS Neptune"""
        nodes = []
        all_tables = self.source_tables.union(self.target_tables)

        # Generate nodes
        for table in all_tables:
            # Clean up table name for label
            table_parts = table.split('.')
            label = table_parts[-1]  # Use last part as label
            nodes.append({
                '~id': table,
                '~label': label,
                'name': table,
                'schema': '.'.join(table_parts[:-1]) if len(table_parts) > 1 else 'default'
            })

        # Generate edges
        edges = []
        for idx, mapping in enumerate(self.mappings):
            edges.append({
                '~id': f'e{idx}',
                '~from': mapping['source'],
                '~to': mapping['target'],
                '~label': 'TO_TARGET'
            })

        # Write files
        with open(nodes_file, 'w') as f:
            for node in nodes:
                f.write(json.dumps(node) + '\n')

        with open(edges_file, 'w') as f:
            for edge in edges:
                f.write(json.dumps(edge) + '\n')


def main():
    """Main function to demonstrate usage"""
    parser = SQLLineageParser()
    parser.process_sql_file('input.sql')
    parser.generate_mapping_csv('mappings.csv')
    parser.generate_neptune_files('nodes.csv', 'edges.csv')


if __name__ == "__main__":
    main()