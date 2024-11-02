What if
Company , Product, Business Product, TEch Product and so on are stores as table with their respcetive properties  are stored in RDMS
- A Company node  has many Product nodes.
- Product nodes are connected to both Business Product and Tech Product nodes.
- Tech Product nodes are connected to multiple Tech Component nodes.
- Business Product nodes are connected to multiple Business Component nodes.
How would i query using SQL and to get the following json to render inD3.js as graph
onst graph = {
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
    ],
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
  };