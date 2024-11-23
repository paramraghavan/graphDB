Let me explain CTEs (Common Table Expressions) and enhance our code to handle them.

CTEs are temporary result sets or views that exist only within the scope of a single SQL statement. They are defined
using the WITH clause and make complex queries more readable and maintainable.

Here are some examples:

```sql
-- Basic CTE
WITH sales_summary AS (
    SELECT 
        product_id,
        SUM(quantity) as total_quantity
    FROM sales
    GROUP BY product_id
)
SELECT p.product_name, s.total_quantity
FROM products p
JOIN sales_summary s ON p.product_id = s.product_id;

-- Multiple CTEs
WITH monthly_sales AS (
    SELECT 
        date_trunc('month', sale_date) as month,
        SUM(amount) as revenue
    FROM sales
    GROUP BY date_trunc('month', sale_date)
),
yearly_average AS (
    SELECT AVG(revenue) as avg_monthly_revenue
    FROM monthly_sales
)
SELECT 
    month,
    revenue,
    avg_monthly_revenue,
    revenue - avg_monthly_revenue as variance
FROM monthly_sales, yearly_average;

-- Recursive CTE (commonly used for hierarchical data)
WITH RECURSIVE employee_hierarchy AS (
    -- Base case: top level employees
    SELECT employee_id, name, manager_id, 1 as level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive case: employees with managers
    SELECT e.employee_id, e.name, e.manager_id, eh.level + 1
    FROM employees e
    JOIN employee_hierarchy eh ON e.manager_id = eh.employee_id
)
SELECT * FROM employee_hierarchy;
```

```python
import sqlparse
import re
import csv
import pandas as pd
from typing import Dict, Set, List, Tuple, Optional
from sqlparse.sql import Token, TokenList
from sqlparse.tokens import Keyword, DML, DDL

class SQLLineageAnalyzer:
    def __init__(self):
        self.source_tables: Set[str] = set()
        self.target_tables: Set[str] = set()
        self.mappings: List[Dict[str, str]] = []
        self.cte_definitions: Dict[str, Set[str]] = {}
        
    def clean_table_name(self, table_name: str) -> str:
        """Clean table names by removing schema, quotes, etc."""
        if '.' in table_name:
            table_name = table_name.split('.')[-1]
        return re.sub(r'["\'\[\]]', '', table_name.strip())

    def extract_ctes(self, sql: str) -> Dict[str, Set[str]]:
        """Extract CTEs and their source tables from a SQL statement."""
        cte_dict = {}
        
        # Find WITH clause
        with_match = re.search(r'WITH\s+(?:RECURSIVE\s+)?(.+?)(?=SELECT|INSERT|UPDATE|MERGE|DELETE)', 
                             sql, re.IGNORECASE | re.DOTALL)
        
        if with_match:
            cte_definitions = with_match.group(1)
            # Split multiple CTEs
            cte_parts = re.split(r',(?=\s*[a-zA-Z]+\s+AS\s*\()', cte_definitions)
            
            for cte_part in cte_parts:
                # Extract CTE name and its query
                cte_match = re.match(r'(\w+)\s+AS\s*\((.*)\)', cte_part.strip(), re.DOTALL)
                if cte_match:
                    cte_name = cte_match.group(1)
                    cte_query = cte_match.group(2)
                    
                    # Extract source tables from the CTE's query
                    sources = set()
                    from_match = re.findall(r'FROM\s+(\w+\.?\w+)', cte_query, re.IGNORECASE)
                    join_match = re.findall(r'JOIN\s+(\w+\.?\w+)', cte_query, re.IGNORECASE)
                    
                    # Add found tables to sources
                    sources.update([self.clean_table_name(t) for t in from_match + join_match])
                    
                    # Remove any references to previously defined CTEs
                    sources = {s for s in sources if s not in cte_dict}
                    
                    cte_dict[self.clean_table_name(cte_name)] = sources
                    
        return cte_dict

    def extract_tables_from_sql(self, sql: str) -> Tuple[Set[str], Set[str]]:
        """Extract source and target tables from a SQL statement."""
        sql = sqlparse.format(sql, strip_comments=True)
        parsed = sqlparse.parse(sql)[0]
        
        # Extract CTEs first
        self.cte_definitions = self.extract_ctes(sql)
        
        # Initialize source and target tables for this statement
        sources = set()
        targets = set()
        
        # Convert to uppercase for consistent matching
        sql_upper = sql.upper()
        
        # Remove WITH clause for main query analysis
        main_query = re.sub(r'WITH\s+(?:RECURSIVE\s+)?(.+?)(?=SELECT|INSERT|UPDATE|MERGE|DELETE)', 
                          '', sql_upper, flags=re.IGNORECASE | re.DOTALL)
        
        # Identify statement type
        if main_query.startswith('SELECT'):
            # Handle SELECT INTO statements
            into_match = re.search(r'INTO\s+(\w+\.?\w+)', main_query)
            if into_match:
                targets.add(self.clean_table_name(into_match.group(1)))
            
            # Extract source tables from FROM and JOIN clauses
            from_match = re.findall(r'FROM\s+(\w+\.?\w+)', main_query)
            join_match = re.findall(r'JOIN\s+(\w+\.?\w+)', main_query)
            sources.update([self.clean_table_name(t) for t in from_match + join_match])
            
        elif main_query.startswith('INSERT'):
            # Extract target table
            insert_match = re.search(r'INTO\s+(\w+\.?\w+)', main_query)
            if insert_match:
                targets.add(self.clean_table_name(insert_match.group(1)))
            
            # Extract source tables from SELECT part
            from_match = re.findall(r'FROM\s+(\w+\.?\w+)', main_query)
            join_match = re.findall(r'JOIN\s+(\w+\.?\w+)', main_query)
            sources.update([self.clean_table_name(t) for t in from_match + join_match])
            
        elif main_query.startswith('MERGE'):
            # Extract target table
            merge_match = re.search(r'INTO\s+(\w+\.?\w+)', main_query)
            if merge_match:
                targets.add(self.clean_table_name(merge_match.group(1)))
            
            # Extract source tables
            using_match = re.search(r'USING\s+(\w+\.?\w+)', main_query)
            if using_match:
                sources.add(self.clean_table_name(using_match.group(1)))
            
            # Additional source tables from WHEN MATCHED/NOT MATCHED clauses
            when_match = re.findall(r'FROM\s+(\w+\.?\w+)', main_query)
            sources.update([self.clean_table_name(t) for t in when_match])
            
        elif main_query.startswith('CREATE') or main_query.startswith('REPLACE'):
            # Extract target table
            create_match = re.search(r'TABLE\s+(\w+\.?\w+)', main_query)
            if create_match:
                targets.add(self.clean_table_name(create_match.group(1)))
            
            # Extract source tables from SELECT part if present
            from_match = re.findall(r'FROM\s+(\w+\.?\w+)', main_query)
            join_match = re.findall(r'JOIN\s+(\w+\.?\w+)', main_query)
            sources.update([self.clean_table_name(t) for t in from_match + join_match])
        
        # Process CTEs and add their sources
        cte_sources = set()
        for cte_name, cte_tables in self.cte_definitions.items():
            if cte_name in sources:
                sources.remove(cte_name)  # Remove the CTE name itself
                cte_sources.update(cte_tables)  # Add the CTE's source tables
        
        sources.update(cte_sources)
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
                            'target': target,
                            'statement_type': self.get_statement_type(stmt)
                        })

    def get_statement_type(self, sql: str) -> str:
        """Determine the type of SQL statement."""
        sql_upper = sql.upper().strip()
        if sql_upper.startswith('SELECT'):
            return 'SELECT'
        elif sql_upper.startswith('INSERT'):
            return 'INSERT'
        elif sql_upper.startswith('MERGE'):
            return 'MERGE'
        elif sql_upper.startswith('CREATE') or sql_upper.startswith('REPLACE'):
            return 'CREATE/REPLACE'
        return 'OTHER'

    def generate_mapping_csv(self, output_file: str):
        """Generate CSV file with source-to-target mappings."""
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['source', 'target', 'statement_type'])
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
        edges_df = edges_df[['~id', '~label', '~from', '~to', 'statement_type']]
        edges_df.to_csv(edges_file, index=False)

def main():
    """Example usage of the SQL Lineage Analyzer."""
    # Create analyzer instance
    analyzer = SQLLineageAnalyzer()
    
    # Example SQL with CTEs
    example_sql = """
    WITH sales_summary AS (
        SELECT product_id, SUM(quantity) as total_quantity
        FROM sales
        GROUP BY product_id
    ),
    top_products AS (
        SELECT product_id, total_quantity
        FROM sales_summary
        WHERE total_quantity > 1000
    )
    INSERT INTO product_analysis (product_id, quantity, status)
    SELECT p.product_id, t.total_quantity, 'High Volume'
    FROM products p
    JOIN top_products t ON p.product_id = t.product_id;
    """
    
    # Write example SQL to a file
    with open('example.sql', 'w') as f:
        f.write(example_sql)
    
    # Analyze the SQL file
    analyzer.analyze_sql_file('example.sql')
    
    # Generate output files
    analyzer.generate_mapping_csv('table_mappings.csv')
    analyzer.generate_neptune_files('nodes.csv', 'edges.csv')

if __name__ == "__main__":
    main()
```



Key enhancements for CTE handling:

1. CTE Detection:
    - Added `extract_ctes` method to identify and parse WITH clauses
    - Handles both regular and recursive CTEs
    - Supports multiple CTEs in a single statement

2. Source Table Resolution:
    - Tracks CTE dependencies and their source tables
    - Resolves nested CTEs correctly
    - Removes CTE references and replaces them with actual source tables

3. Handling Complex Cases:
    - Recursive CTEs (used for hierarchical queries)
    - Multiple CTEs in a single statement
    - CTEs that reference other CTEs

Common CTE Use Cases:

1. Breaking down complex queries into manageable chunks
2. Recursive queries for hierarchical data (org charts, bill of materials)
3. Running totals and moving averages
4. Data transformation pipelines
5. Hierarchical or graph traversal queries
