# Supplu chain knowledge graph

A knowledge graph for a supply chain execution inventory alert system involves representing various entities such as
warehouses, products, and shipments, and their relationships such as inventory levels, replenishment needs, and 
shipment statuses.

## Vertices/Entities
- Warehouses: WarehouseA, WarehouseB, WarehouseC
- Products: Product1, Product2, Product3
- Shipments: Shipment1, Shipment2, Shipment3


## Edges/Relationships
- Inventory Levels: Linking products to warehouses with inventory levels.
- Replenishment Needs: Indicating which products in which warehouses need replenishment.
- Shipment Statuses: Linking shipments to products and indicating their status (e.g., In Transit, Delivered).

## Create Graph

```gremlin
// Add Warehouse vertices
g.addV('warehouse').property('name', 'WarehouseA').as('warehouseA')
g.addV('warehouse').property('name', 'WarehouseB').as('warehouseB')
g.addV('warehouse').property('name', 'WarehouseC').as('warehouseC')

// Add Product vertices
g.addV('product').property('name', 'Product1').as('product1')
g.addV('product').property('name', 'Product2').as('product2')
g.addV('product').property('name', 'Product3').as('product3')

// Add Shipment vertices
g.addV('shipment').property('name', 'Shipment1').as('shipment1')
g.addV('shipment').property('name', 'Shipment2').as('shipment2')
g.addV('shipment').property('name', 'Shipment3').as('shipment3')

// Add Inventory Level edges
g.addE('inventory_level').from('product1').to('warehouseA').property('quantity', 100)
g.addE('inventory_level').from('product2').to('warehouseB').property('quantity', 50)
// ... more inventory levels

// Add Replenishment Need edges
g.addE('needs_replenishment').from('warehouseA').to('product1').property('minimum_quantity', 150)
// ... more replenishment needs

// Add Shipment Status edges
g.addE('shipment_status').from('shipment1').to('product1').property('status', 'In Transit')
// ... more shipment statuses
```

## Query
- Find products with low inventory in a specific warehouse:
- query identifies products in WarehouseA that need replenishment.
```gremlin
g.V().has('warehouse', 'name', 'WarehouseA').out('needs_replenishment').values('name')
```

- List all shipments in transit for a specific product:
- query returns the names of all shipments that are currently in transit for Product1.
```gremlin
g.V().has('product', 'name', 'Product1').in('shipment_status').has('status', 'In Transit').values('name')

```

- Determine the inventory level of a product in all warehouses:
- query provides the inventory levels of Product1 across all warehouses.
```gremlin
g.V().has('product', 'name', 'Product1').out('inventory_level').project('warehouse', 'quantity').by('name').by('quantity')

```

- Identify which shipments are affecting inventory levels of a warehouse:
```gremlin
g.V().has('warehouse', 'name', 'WarehouseB').in('inventory_level').out('shipment_status').values('name')

```
