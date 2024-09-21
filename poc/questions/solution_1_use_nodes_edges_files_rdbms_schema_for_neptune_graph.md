
# RDBMS Schema and SQL Queries for Neptune Graph Data

## Schema Design:

### 1. Nodes Table:
This table will store the graph's nodes (vertices), including attributes such as `id`, `label`, `name`, and `depth`.

```sql
CREATE TABLE nodes (
  id VARCHAR(255) PRIMARY KEY,   -- Unique identifier for each node
  label VARCHAR(255),            -- The type of node (e.g., Company, Product)
  name VARCHAR(255),             -- The name of the node (e.g., Product A)
  depth INT                      -- The depth or level of the node in the hierarchy
);
```

### 2. Links Table:
This table will represent the edges (relationships) between the nodes, with attributes for the source node, target node, and relationship label.

```sql
CREATE TABLE links (
  id SERIAL PRIMARY KEY,         -- Unique identifier for each link
  source_id VARCHAR(255),        -- The source node ID (foreign key to nodes table)
  target_id VARCHAR(255),        -- The target node ID (foreign key to nodes table)
  label VARCHAR(255),            -- The label or type of relationship (e.g., "has", "includes")
  FOREIGN KEY (source_id) REFERENCES nodes(id),
  FOREIGN KEY (target_id) REFERENCES nodes(id)
);
```

## SQL Queries to Insert Data:

### 1. Inserting Nodes into the `nodes` Table:
For each node in the `graph.nodes` array, you will insert a row into the `nodes` table.

```sql
INSERT INTO nodes (id, label, name, depth)
VALUES ('company1', 'Company', 'TechCorp', 0),
       ('product1', 'Product', 'Product A', 1),
       ('product2', 'Product', 'Product B', 1),
       ('business_product1', 'Business Product', 'Business Product A1', 2),
       ('business_product2', 'Business Product', 'Business Product A2', 2),
       ('tech_product1', 'Tech Product', 'Tech Product B1', 2),
       ('tech_product2', 'Tech Product', 'Tech Product B2', 2),
       ('tech_component1', 'Tech Component', 'Tech Component B1.1', 3),
       ('tech_component2', 'Tech Component', 'Tech Component B1.2', 3),
       ('business_component1', 'Business Component', 'Business Component A1.1', 3),
       ('business_component2', 'Business Component', 'Business Component A1.2', 3);
```

### 2. Inserting Links into the `links` Table:
For each link in the `graph.links` array, you'll insert a row into the `links` table.

```sql
INSERT INTO links (source_id, target_id, label)
VALUES ('company1', 'product1', 'has'),
       ('company1', 'product2', 'has'),
       ('product1', 'business_product1', 'includes'),
       ('product1', 'business_product2', 'includes'),
       ('product2', 'tech_product1', 'includes'),
       ('product2', 'tech_product2', 'includes'),
       ('business_product1', 'business_component1', 'has'),
       ('business_product1', 'business_component2', 'has'),
       ('tech_product1', 'tech_component1', 'has'),
       ('tech_product1', 'tech_component2', 'has');
```

## Full Schema and Example SQL Script:

### 1. Schema Creation:

```sql
-- Create the table to store nodes (vertices)
CREATE TABLE nodes (
  id VARCHAR(255) PRIMARY KEY,   -- Node ID (Unique)
  label VARCHAR(255),            -- Node label (type: Company, Product, etc.)
  name VARCHAR(255),             -- Node name
  depth INT                      -- Depth level of the node
);

-- Create the table to store links (edges)
CREATE TABLE links (
  id SERIAL PRIMARY KEY,         -- Unique link ID (auto-increment)
  source_id VARCHAR(255),        -- Source node ID
  target_id VARCHAR(255),        -- Target node ID
  label VARCHAR(255),            -- Type of relationship (has, includes, etc.)
  FOREIGN KEY (source_id) REFERENCES nodes(id),
  FOREIGN KEY (target_id) REFERENCES nodes(id)
);
```

### 2. Insert Nodes:

```sql
-- Insert data into nodes table
INSERT INTO nodes (id, label, name, depth)
VALUES ('company1', 'Company', 'TechCorp', 0),
       ('product1', 'Product', 'Product A', 1),
       ('product2', 'Product', 'Product B', 1),
       ('business_product1', 'Business Product', 'Business Product A1', 2),
       ('business_product2', 'Business Product', 'Business Product A2', 2),
       ('tech_product1', 'Tech Product', 'Tech Product B1', 2),
       ('tech_product2', 'Tech Product', 'Tech Product B2', 2),
       ('tech_component1', 'Tech Component', 'Tech Component B1.1', 3),
       ('tech_component2', 'Tech Component', 'Tech Component B1.2', 3),
       ('business_component1', 'Business Component', 'Business Component A1.1', 3),
       ('business_component2', 'Business Component', 'Business Component A1.2', 3);
```

### 3. Insert Links:

```sql
-- Insert data into links table
INSERT INTO links (source_id, target_id, label)
VALUES ('company1', 'product1', 'has'),
       ('company1', 'product2', 'has'),
       ('product1', 'business_product1', 'includes'),
       ('product1', 'business_product2', 'includes'),
       ('product2', 'tech_product1', 'includes'),
       ('product2', 'tech_product2', 'includes'),
       ('business_product1', 'business_component1', 'has'),
       ('business_product1', 'business_component2', 'has'),
       ('tech_product1', 'tech_component1', 'has'),
       ('tech_product1', 'tech_component2', 'has');
```

## Querying the Data:

- **Get All Nodes**:
  
  ```sql
  SELECT * FROM nodes;
  ```

- **Get All Links**:

  ```sql
  SELECT * FROM links;
  ```

- **Get All Products** (Depth 1):
  
  ```sql
  SELECT * FROM nodes WHERE depth = 1;
  ```

- **Get Components Linked to a Specific Product**:

  ```sql
  SELECT target_id, label
  FROM links
  WHERE source_id = 'product1';
  ```
