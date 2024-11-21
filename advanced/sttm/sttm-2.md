Create a Python script that analyzes SQL statements to generate a source-to-target mapping and create a graph-friendly format for Neptune DB.



```python
import sqlparse
import re
import csv
import uuid
from pathlib import Path

def extract_table_names(sql_text):
    """Extract table names from SQL statement."""
    # Parse the SQL statement
    parsed = sqlparse.parse(sql_text)[0]
    
    source_tables = set()
    target_tables = set()
    
    # Convert to uppercase for consistent matching
    sql_type = parsed.get_type().upper()
    
    # Skip DELETE statements
    if sql_type == 'DELETE':
        return [], []
    
    # Extract table names based on SQL type
    if sql_type in ('SELECT', 'INSERT', 'MERGE'):
        for token in parsed.tokens:
            # Convert token to string for analysis
            token_str = str(token)
            
            # Handle different SQL types
            if sql_type == 'SELECT':
                # Find tables after FROM and JOIN
                if re.search(r'\bFROM\b|\bJOIN\b', token_str, re.IGNORECASE):
                    tables = re.findall(r'\b([A-Za-z0-9_$.]+)\b', token_str)
                    source_tables.update(tables)
            
            elif sql_type == 'INSERT':
                # Find target table (first table after INSERT INTO)
                if re.search(r'\bINTO\b', token_str, re.IGNORECASE):
                    target = re.search(r'\bINTO\s+([A-Za-z0-9_$.]+)', token_str, re.IGNORECASE)
                    if target:
                        target_tables.add(target.group(1))
                # Find source tables after FROM
                if re.search(r'\bFROM\b', token_str, re.IGNORECASE):
                    tables = re.findall(r'\b([A-Za-z0-9_$.]+)\b', token_str)
                    source_tables.update(tables)
            
            elif sql_type == 'MERGE':
                # Find target table (first table after MERGE INTO)
                if re.search(r'\bINTO\b', token_str, re.IGNORECASE):
                    target = re.search(r'\bINTO\s+([A-Za-z0-9_$.]+)', token_str, re.IGNORECASE)
                    if target:
                        target_tables.add(target.group(1))
                # Find source tables after USING
                if re.search(r'\bUSING\b', token_str, re.IGNORECASE):
                    tables = re.findall(r'\b([A-Za-z0-9_$.]+)\b', token_str)
                    source_tables.update(tables)
    
    # Clean up table names
    source_tables = {table for table in source_tables if table.upper() not in ('SELECT', 'FROM', 'JOIN', 'WHERE', 'AND', 'OR')}
    target_tables = {table for table in target_tables if table.upper() not in ('INTO', 'VALUES')}
    
    return list(source_tables), list(target_tables)

def process_sql_files(directory_path):
    """Process all SQL files in the given directory."""
    # Store all relationships
    relationships = []
    unique_tables = set()
    
    # Process each SQL file
    for sql_file in Path(directory_path).glob('**/*.sql'):
        with open(sql_file, 'r') as f:
            sql_content = f.read()
            
            # Split into individual SQL statements
            statements = sqlparse.split(sql_content)
            
            for statement in statements:
                source_tables, target_tables = extract_table_names(statement)
                
                # Add to unique tables set
                unique_tables.update(source_tables)
                unique_tables.update(target_tables)
                
                # Create relationships
                for source in source_tables:
                    for target in target_tables:
                        relationships.append({
                            'id': str(uuid.uuid4()),
                            'from': source,
                            'to': target
                        })
    
    return relationships, unique_tables

def generate_output_files(relationships, unique_tables, output_dir):
    """Generate CSV files for source-target mapping and Neptune DB format."""
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate source-target mapping CSV
    mapping_file = Path(output_dir) / 'source_target_mapping.csv'
    with open(mapping_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Source', 'Target'])
        for rel in relationships:
            writer.writerow([rel['from'], rel['to']])
    
    # Generate Neptune nodes CSV
    nodes_file = Path(output_dir) / 'neptune_nodes.csv'
    with open(nodes_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['~id', 'name'])
        for table in unique_tables:
            writer.writerow([str(uuid.uuid4()), table])
    
    # Generate Neptune edges CSV
    edges_file = Path(output_dir) / 'neptune_edges.csv'
    with open(edges_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['~id', '~from', '~to'])
        for rel in relationships:
            writer.writerow([rel['id'], rel['from'], rel['to']])

def main():
    # Configuration
    sql_directory = './sql_files'  # Directory containing SQL files
    output_directory = './output'  # Directory for output files
    
    # Process SQL files
    relationships, unique_tables = process_sql_files(sql_directory)
    
    # Generate output files
    generate_output_files(relationships, unique_tables, output_directory)
    
    print(f"Processing complete. Found {len(unique_tables)} unique tables and {len(relationships)} relationships.")

if __name__ == "__main__":
    main()

```

I've created a Python script that:

1. Processes SQL files and extracts table relationships from SELECT, INSERT, and MERGE statements (skipping DELETE statements)
2. Handles various SQL syntax patterns including:
   - SELECT statements with FROM and JOIN clauses
   - INSERT statements with source and target tables
   - MERGE statements with INTO and USING clauses
3. Generates three output files:
   - source_target_mapping.csv: Simple source-to-target table mapping
   - neptune_nodes.csv: Node list for Neptune DB with unique table names
   - neptune_edges.csv: Edge list for Neptune DB with relationships

To use the script:

1. Install required packages:
```bash
pip install sqlparse
```

2. Place your SQL files in a directory (default: ./sql_files)
3. Run the script:
```bash
python sql_mapping_extractor.py
```

The script uses:
- sqlparse for reliable SQL parsing
- regex for table name extraction
- UUID generation for Neptune DB IDs
- Path from pathlib for cross-platform file handling
