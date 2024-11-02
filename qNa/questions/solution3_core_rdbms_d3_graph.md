
# SQL Schema and Query for RDBMS to D3.js JSON Graph

## Scenario:
- A **Company** node has many **Product** nodes.
- **Product** nodes are connected to both **Business Product** and **Tech Product** nodes.
- **Tech Product** nodes are connected to multiple **Tech Component** nodes.
- **Business Product** nodes are connected to multiple **Business Component** nodes.

## SQL Schema:

### 1. **company table**:
```sql
CREATE TABLE company (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255)
);
```

### 2. **product table**:
```sql
CREATE TABLE product (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255),
  company_id VARCHAR(255),
  FOREIGN KEY (company_id) REFERENCES company(id)
);
```

### 3. **business_product table**:
```sql
CREATE TABLE business_product (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255),
  product_id VARCHAR(255),
  FOREIGN KEY (product_id) REFERENCES product(id)
);
```

### 4. **tech_product table**:
```sql
CREATE TABLE tech_product (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255),
  product_id VARCHAR(255),
  FOREIGN KEY (product_id) REFERENCES product(id)
);
```

### 5. **business_component table**:
```sql
CREATE TABLE business_component (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255),
  business_product_id VARCHAR(255),
  FOREIGN KEY (business_product_id) REFERENCES business_product(id)
);
```

### 6. **tech_component table**:
```sql
CREATE TABLE tech_component (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255),
  tech_product_id VARCHAR(255),
  FOREIGN KEY (tech_product_id) REFERENCES tech_product(id)
);
```

## SQL Query:

### 1. **Nodes Query**:
```sql
SELECT id, 'Company' AS label, name, 0 AS depth
FROM company
UNION
SELECT id, 'Product' AS label, name, 1 AS depth
FROM product
UNION
SELECT id, 'Business Product' AS label, name, 2 AS depth
FROM business_product
UNION
SELECT id, 'Tech Product' AS label, name, 2 AS depth
FROM tech_product
UNION
SELECT id, 'Business Component' AS label, name, 3 AS depth
FROM business_component
UNION
SELECT id, 'Tech Component' AS label, name, 3 AS depth
FROM tech_component;
```

### 2. **Links Query**:
```sql
SELECT company.id AS source, product.id AS target, 'has' AS label
FROM company
JOIN product ON company.id = product.company_id
UNION
SELECT product.id AS source, business_product.id AS target, 'includes' AS label
FROM product
JOIN business_product ON product.id = business_product.product_id
UNION
SELECT product.id AS source, tech_product.id AS target, 'includes' AS label
FROM product
JOIN tech_product ON product.id = tech_product.product_id
UNION
SELECT business_product.id AS source, business_component.id AS target, 'has' AS label
FROM business_product
JOIN business_component ON business_product.id = business_component.business_product_id
UNION
SELECT tech_product.id AS source, tech_component.id AS target, 'has' AS label
FROM tech_product
JOIN tech_component ON tech_product.id = tech_component.tech_product_id;
```

## JSON Output Example:

### Nodes JSON:
```json
{
  "nodes": [
    {"id": "company1", "label": "Company", "name": "TechCorp", "depth": 0},
    {"id": "product1", "label": "Product", "name": "Product A", "depth": 1},
    {"id": "product2", "label": "Product", "name": "Product B", "depth": 1},
    {"id": "business_product1", "label": "Business Product", "name": "Business Product A1", "depth": 2},
    {"id": "business_product2", "label": "Business Product", "name": "Business Product A2", "depth": 2},
    {"id": "tech_product1", "label": "Tech Product", "name": "Tech Product B1", "depth": 2},
    {"id": "tech_product2", "label": "Tech Product", "name": "Tech Product B2", "depth": 2},
    {"id": "tech_component1", "label": "Tech Component", "name": "Tech Component B1.1", "depth": 3},
    {"id": "tech_component2", "label": "Tech Component", "name": "Tech Component B1.2", "depth": 3},
    {"id": "business_component1", "label": "Business Component", "name": "Business Component A1.1", "depth": 3},
    {"id": "business_component2", "label": "Business Component", "name": "Business Component A1.2", "depth": 3}
  ]
}
```

### Links JSON:
```json
{
  "links": [
    {"source": "company1", "target": "product1", "label": "has"},
    {"source": "company1", "target": "product2", "label": "has"},
    {"source": "product1", "target": "business_product1", "label": "includes"},
    {"source": "product1", "target": "business_product2", "label": "includes"},
    {"source": "product2", "target": "tech_product1", "label": "includes"},
    {"source": "product2", "target": "tech_product2", "label": "includes"},
    {"source": "business_product1", "target": "business_component1", "label": "has"},
    {"source": "business_product1", "target": "business_component2", "label": "has"},
    {"source": "tech_product1", "target": "tech_component1", "label": "has"},
    {"source": "tech_product1", "target": "tech_component2", "label": "has"}
  ]
}
```

### Querying the Data:
- **Get All Nodes**:
```sql
SELECT * FROM nodes;
```

- **Get All Links**:
```sql
SELECT * FROM links;
```

- **Get All Products (Depth 1)**:
```sql
SELECT * FROM nodes WHERE depth = 1;
```

- **Get Components Linked to a Specific Product**:
```sql
SELECT target_id, label
FROM links
WHERE source_id = 'product1';
```
