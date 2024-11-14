A Python script that can analyze SQL statements to generate a STTM - source-to-target mapping
and prepare data for Neptune DB graph representation.


```python
import re
import csv
import sqlparse
from collections import defaultdict
import uuid

class SQLLineageExtractor:
    def __init__(self):
        self.relationships = []
        self.all_tables = set()
        
    def extract_tables(self, sql):
        """Extract table names from SQL statement"""
        # Parse the SQL statement
        parsed = sqlparse.parse(sql.strip())[0]
        
        # Initialize source and target tables
        source_tables = set()
        target_tables = set()
        
        # Convert to uppercase for consistent matching
        sql_upper = sql.upper()
        
        # Skip DELETE statements
        if sql_upper.strip().startswith('DELETE'):
            return
            
        # Identify statement type and extract tables
        if sql_upper.strip().startswith('INSERT'):
            # Extract target table (first table after INSERT INTO)
            target_match = re.search(r'INSERT\s+INTO\s+([^\s\(]+)', sql_upper)
            if target_match:
                target_tables.add(target_match.group(1))
            
            # Extract source tables from SELECT part
            source_match = re.findall(r'FROM\s+([^\s\,\)]+)|JOIN\s+([^\s\,\)]+)', sql_upper)
            for match in source_match:
                source_tables.update(t for t in match if t)
                
        elif sql_upper.strip().startswith('MERGE'):
            # Extract target table (first table after MERGE INTO)
            target_match = re.search(r'MERGE\s+INTO\s+([^\s\(]+)', sql_upper)
            if target_match:
                target_tables.add(target_match.group(1))
            
            # Extract source tables (after USING)
            source_match = re.search(r'USING\s+([^\s\(]+)', sql_upper)
            if source_match:
                source_tables.add(source_match.group(1))
                
        elif sql_upper.strip().startswith('SELECT'):
            # For standalone SELECT, consider all tables as source
            source_match = re.findall(r'FROM\s+([^\s\,\)]+)|JOIN\s+([^\s\,\)]+)', sql_upper)
            for match in source_match:
                source_tables.update(t for t in match if t)
        
        # Clean table names
        source_tables = {self.clean_table_name(t) for t in source_tables}
        target_tables = {self.clean_table_name(t) for t in target_tables}
        
        # Update all_tables set
        self.all_tables.update(source_tables)
        self.all_tables.update(target_tables)
        
        # Create relationships
        for source in source_tables:
            for target in target_tables:
                self.relationships.append({
                    'id': str(uuid.uuid4()),
                    'from': source,
                    'to': target
                })
    
    def clean_table_name(self, table_name):
        """Clean table name by removing schema, quotes, etc."""
        # Remove quotes
        table_name = table_name.strip('"').strip("'")
        # Take last part if schema qualified
        return table_name.split('.')[-1]
    
    def process_sql_file(self, file_path):
        """Process a file containing SQL statements"""
        try:
            with open(file_path, 'r') as file:
                sql_content = file.read()
                # Split into individual statements
                statements = sqlparse.split(sql_content)
                for stmt in statements:
                    if stmt.strip():
                        self.extract_tables(stmt)
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
    
    def generate_csv_outputs(self):
        """Generate CSV files for nodes and edges"""
        # Write relationships (edges) file
        with open('table_relationships.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'from', 'to'])
            writer.writeheader()
            writer.writerows(self.relationships)
        
        # Write nodes file
        with open('table_nodes.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'label'])
            writer.writeheader()
            for table in self.all_tables:
                writer.writerow({
                    'id': table,
                    'label': table
                })

def main(sql_files):
    """Main function to process multiple SQL files"""
    extractor = SQLLineageExtractor()
    
    # Process each SQL file
    for file_path in sql_files:
        extractor.process_sql_file(file_path)
    
    # Generate CSV outputs
    extractor.generate_csv_outputs()

if __name__ == "__main__":
    # Example usage
    sql_files = ['path/to/your/sql/files/*.sql']  # Replace with actual file paths
    main(sql_files)

```

This script will help you:

1. Process multiple SQL files
2. Extract table names from SELECT, INSERT, and MERGE statements (skipping DELETE statements)
3. Generate two CSV files:
   - `table_nodes.csv`: Contains all unique tables
   - `table_relationships.csv`: Contains edges showing relationships between source and target tables

To use the script:

1. Install required packages:
```bash
pip install sqlparse
```

2. Use it like this:
```python
sql_files = ['path/to/file1.sql', 'path/to/file2.sql']
main(sql_files)
```

The script handles:
- Different SQL statement types (SELECT, INSERT, MERGE)
- Schema-qualified table names
- Quoted identifiers
- Multiple source tables (FROM and JOIN clauses)
- UUID generation for relationship IDs
- Error handling for file processing