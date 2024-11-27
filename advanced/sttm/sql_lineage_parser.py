import sqlparse
import re
import csv
import json
from collections import defaultdict


class SQLLineageParser:
    def __init__(self):
        self.source_targets = defaultdict(set)
        self.all_tables = set()

    def extract_table_names(self, sql):
        """Extract table names from SQL statement using regex patterns."""
        # Remove comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

        # Pattern for fully qualified table names
        table_pattern = r'(?:FROM|JOIN|INTO|UPDATE|MERGE INTO)\s+([a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+){0,2}\.?[a-zA-Z0-9_]+)'

        tables = re.finditer(table_pattern, sql, re.IGNORECASE)
        return [t.group(1).strip() for t in tables]

    def parse_sql_file(self, file_path):
        """Parse SQL file and build source-target mappings."""
        with open(file_path, 'r') as f:
            sql_content = f.read()

        # Split into individual statements
        statements = sqlparse.split(sql_content)

        for statement in statements:
            statement = statement.strip()
            if not statement:
                continue

            # Skip DELETE statements
            if statement.upper().startswith('DELETE'):
                continue

            parsed = sqlparse.parse(statement)[0]

            # Handle different types of statements
            if self._is_create_or_insert(parsed):
                target_table = self._extract_target_table(parsed)
                source_tables = self._extract_source_tables(statement)

                if target_table and source_tables:
                    self.all_tables.add(target_table)
                    for source in source_tables:
                        self.all_tables.add(source)
                        self.source_targets[target_table].add(source)

    def _is_create_or_insert(self, parsed_stmt):
        """Check if statement is CREATE/INSERT/MERGE."""
        first_token = parsed_stmt.get_type()
        return first_token in ('CREATE', 'INSERT', 'MERGE')

    def _extract_target_table(self, parsed_stmt):
        """Extract target table from CREATE/INSERT/MERGE statement."""
        # Implementation depends on statement type
        stmt_type = parsed_stmt.get_type()

        if stmt_type == 'CREATE':
            # Find table name after CREATE TABLE
            for token in parsed_stmt.tokens:
                if token.is_keyword and token.value.upper() == 'TABLE':
                    idx = parsed_stmt.token_index(token)
                    if idx + 1 < len(parsed_stmt.tokens):
                        return str(parsed_stmt.tokens[idx + 1])

        return None

    def _extract_source_tables(self, sql):
        """Extract source tables from SQL statement."""
        return self.extract_table_names(sql)

    def generate_mapping_csv(self, output_file):
        """Generate CSV file with source-target mappings."""
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Target Table', 'Source Table'])

            for target, sources in self.source_targets.items():
                for source in sources:
                    writer.writerow([target, source])

    def generate_neptune_files(self, nodes_file, edges_file):
        """Generate Neptune-compatible nodes and edges files."""
        # Generate nodes file
        nodes = []
        for table in self.all_tables:
            nodes.append({
                '~id': table,
                '~label': table.split('.')[-1],
                'fullName': table
            })

        with open(nodes_file, 'w') as f:
            for node in nodes:
                f.write(json.dumps(node) + '\n')

        # Generate edges file
        edges = []
        edge_id = 0
        for target, sources in self.source_targets.items():
            for source in sources:
                edges.append({
                    '~id': f'e{edge_id}',
                    '~from': source,
                    '~to': target,
                    '~label': 'TO_TARGET'
                })
                edge_id += 1

        with open(edges_file, 'w') as f:
            for edge in edges:
                f.write(json.dumps(edge) + '\n')


def main():
    # Example usage
    parser = SQLLineageParser()
    parser.parse_sql_file('input.sql')

    # Generate mapping CSV
    parser.generate_mapping_csv('table_mappings.csv')

    # Generate Neptune files
    parser.generate_neptune_files('nodes.json', 'edges.json')


if __name__ == '__main__':
    main()