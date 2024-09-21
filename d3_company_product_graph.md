
# D3.js Visualization of Company, Products, and Components

This example visualizes the relationships between a company, its products, and their respective business and tech components using D3.js.

## JSON Data

```json
{
  "nodes": [
    {"id": "company1", "label": "Company", "name": "TechCorp"},
    {"id": "product1", "label": "Product", "name": "Product A"},
    {"id": "product2", "label": "Product", "name": "Product B"},
    {"id": "business_product1", "label": "Business Product", "name": "Business Product A1"},
    {"id": "business_product2", "label": "Business Product", "name": "Business Product A2"},
    {"id": "tech_product1", "label": "Tech Product", "name": "Tech Product B1"},
    {"id": "tech_product2", "label": "Tech Product", "name": "Tech Product B2"},
    {"id": "tech_component1", "label": "Tech Component", "name": "Tech Component B1.1"},
    {"id": "tech_component2", "label": "Tech Component", "name": "Tech Component B1.2"},
    {"id": "business_component1", "label": "Business Component", "name": "Business Component A1.1"},
    {"id": "business_component2", "label": "Business Component", "name": "Business Component A1.2"}
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
}
```

## D3.js Code

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Company Product Graph</title>
  <script src="https://d3js.org/d3.v5.min.js"></script>
  <style>
    .node {
      stroke: #fff;
      stroke-width: 1.5px;
    }
    .link {
      stroke: #999;
      stroke-opacity: 0.6;
    }
    text {
      font-family: sans-serif;
      font-size: 10px;
      fill: #000;
    }
  </style>
</head>
<body>
  <svg width="800" height="600"></svg>

  <script>
    const width = 800, height = 600;

    // Load JSON data for nodes and links
    const graph = {
      "nodes": [
        {"id": "company1", "label": "Company", "name": "TechCorp"},
        {"id": "product1", "label": "Product", "name": "Product A"},
        {"id": "product2", "label": "Product", "name": "Product B"},
        {"id": "business_product1", "label": "Business Product", "name": "Business Product A1"},
        {"id": "business_product2", "label": "Business Product", "name": "Business Product A2"},
        {"id": "tech_product1", "label": "Tech Product", "name": "Tech Product B1"},
        {"id": "tech_product2", "label": "Tech Product", "name": "Tech Product B2"},
        {"id": "tech_component1", "label": "Tech Component", "name": "Tech Component B1.1"},
        {"id": "tech_component2", "label": "Tech Component", "name": "Tech Component B1.2"},
        {"id": "business_component1", "label": "Business Component", "name": "Business Component A1.1"},
        {"id": "business_component2", "label": "Business Component", "name": "Business Component A1.2"}
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

    const svg = d3.select("svg");
    const simulation = d3.forceSimulation(graph.nodes)
      .force("link", d3.forceLink(graph.links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-500))
      .force("center", d3.forceCenter(width / 2, height / 2));

    // Draw links
    const link = svg.append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(graph.links)
      .enter().append("line")
      .attr("class", "link")
      .attr("stroke-width", 2);

    // Draw nodes
    const node = svg.append("g")
      .attr("class", "nodes")
      .selectAll("circle")
      .data(graph.nodes)
      .enter().append("circle")
      .attr("class", "node")
      .attr("r", 10)
      .attr("fill", "blue")
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    // Add labels to nodes
    const labels = svg.append("g")
      .attr("class", "labels")
      .selectAll("text")
      .data(graph.nodes)
      .enter().append("text")
      .attr("x", 12)
      .attr("y", ".31em")
      .text(d => d.name);

    // Update simulation on each tick
    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

      labels
        .attr("x", d => d.x)
        .attr("y", d => d.y);
    });

    function dragstarted(d) {
      if (!d3.event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(d) {
      d.fx = d3.event.x;
      d.fy = d3.event.y;
    }

    function dragended(d) {
      if (!d3.event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  </script>
</body>
</html>
```
