
# Neptune to D3.js Visualization

To read Amazon Neptune nodes and edges into JSON format for visualization with D3.js, you can retrieve the graph data from Neptune and format it into a structure that D3.js can work with. D3 typically expects a graph structure like:

```json
{
  "nodes": [
    {"id": "node1", "label": "Node 1"},
    {"id": "node2", "label": "Node 2"}
  ],
  "links": [
    {"source": "node1", "target": "node2", "label": "Edge Label"}
  ]
}
```

## 1. Query Neptune for Nodes and Edges

You'll need to write a Gremlin query that fetches the nodes and edges from your Neptune graph. For example:

```gremlin
g.V().as('node').outE().as('edge').inV().select('node', 'edge')
```

This query gets both the nodes and edges from the graph.

## 2. Execute the Query and Retrieve Results

You can use Python and `gremlinpython` to submit the query and process the result:

```python
from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

# Connect to Neptune
neptune_endpoint = 'wss://<your-neptune-endpoint>:8182/gremlin'
connection = DriverRemoteConnection(neptune_endpoint, 'g')
graph = Graph()
g = graph.traversal().withRemote(connection)

# Fetch nodes and edges
query = g.V().as('node').outE().as('edge').inV().select('node', 'edge')
result = g.V().as('node').outE().as('edge').inV().select('node', 'edge').toList()

connection.close()
```

## 3. Format the Result for D3.js

The next step is to transform the result into the `nodes` and `links` structure expected by D3.js.

```python
import json

# Create lists to store nodes and edges
nodes = []
edges = []

# Process the result to extract nodes and edges
for item in result:
    node = item['node']
    edge = item['edge']

    # Add nodes
    node_id = node.id
    if node_id not in [n['id'] for n in nodes]:
        nodes.append({'id': node_id, 'label': node.label})

    # Add edges
    edges.append({
        'source': edge.outV.id,
        'target': edge.inV.id,
        'label': edge.label
    })

# Create the D3.js compatible JSON structure
graph_data = {
    'nodes': nodes,
    'links': edges
}

# Convert to JSON
graph_json = json.dumps(graph_data, indent=2)

# Print or save to file
print(graph_json)

with open('graph_data.json', 'w') as f:
    f.write(graph_json)
```

## 4. Integrating with D3.js

Once you have the JSON data, you can load it into a D3.js visualization. In your HTML file:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://d3js.org/d3.v5.min.js"></script>
  <title>Neptune Graph</title>
</head>
<body>
  <svg width="800" height="600"></svg>

  <script>
    // Load the JSON data
    d3.json('graph_data.json').then(function(data) {
      const svg = d3.select("svg"),
            width = +svg.attr("width"),
            height = +svg.attr("height");

      // Set up simulation
      const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).id(d => d.id))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2));

      // Add links (edges)
      const link = svg.append("g")
          .attr("class", "links")
        .selectAll("line")
        .data(data.links)
        .enter().append("line");

      // Add nodes
      const node = svg.append("g")
          .attr("class", "nodes")
        .selectAll("circle")
        .data(data.nodes)
        .enter().append("circle")
          .attr("r", 5);

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
      });
    });
  </script>
</body>
</html>
```

## Summary of Steps:

1. Query Neptune for nodes and edges.
2. Extract and format the nodes and edges into the JSON structure that D3.js expects.
3. Use the formatted JSON to render the graph in a D3.js force-directed graph.
