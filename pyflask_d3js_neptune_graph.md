
# Render Neptune Query as Graph using PyFlask, D3.js, and NeptuneDB

This guide demonstrates how to render a graph from Amazon Neptune using PyFlask, D3.js, and NeptuneDB. The graph visualization is structured to show the relationships from root to child nodes in a left-to-right format.

## 1. PyFlask Backend (app.py)

Below is the Flask app that interacts with NeptuneDB and serves graph data in a D3.js-compatible format.

```python
from flask import Flask, jsonify, render_template
from gremlin_python.driver import client, serializer

app = Flask(__name__)

# Create a Gremlin client to connect to NeptuneDB
neptune_client = client.Client(
    'wss://<neptune-endpoint>:8182/gremlin',
    'g',
    message_serializer=serializer.GraphSONSerializersV3d0()
)

@app.route('/graph', methods=['GET'])
def get_graph():
    query = '''
    g.V().hasLabel('rootNode').outE().inV().path()
    '''
    # Execute the Gremlin query
    try:
        result = neptune_client.submitAsync(query).result().all().result()
        # Transform the result into a format D3.js can handle
        graph_data = parse_neptune_result(result)
        return jsonify(graph_data)
    except Exception as e:
        return jsonify({"error": str(e)})

def parse_neptune_result(result):
    nodes = []
    edges = []

    for path in result:
        path_objects = path['objects']
        for i in range(len(path_objects) - 1):
            source = path_objects[i]
            target = path_objects[i + 1]
            # Append nodes and edges to the respective lists
            nodes.append({'id': source['id'], 'label': source['label']})
            edges.append({'source': source['id'], 'target': target['id']})

    # Return as a dictionary in D3.js format
    return {"nodes": nodes, "links": edges}

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```

## 2. D3.js Frontend (index.html)

In this template, D3.js is used to visualize the graph data from the PyFlask backend.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeptuneDB Graph Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        svg {
            width: 100%;
            height: 600px;
        }
        .link {
            stroke: #999;
            stroke-opacity: 0.6;
        }
        .node circle {
            fill: #666;
            stroke-width: 1.5px;
        }
        text {
            font: 10px sans-serif;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <svg></svg>

    <script>
        // Fetch graph data from the PyFlask backend
        fetch('/graph')
            .then(response => response.json())
            .then(data => {
                const nodes = data.nodes;
                const links = data.links;

                // Set up SVG and force simulation
                const svg = d3.select("svg");
                const width = +svg.attr("width");
                const height = +svg.attr("height");

                const simulation = d3.forceSimulation(nodes)
                    .force("link", d3.forceLink(links).id(d => d.id).distance(100))
                    .force("charge", d3.forceManyBody().strength(-400))
                    .force("center", d3.forceCenter(width / 2, height / 2));

                // Draw links (edges)
                const link = svg.append("g")
                    .attr("class", "links")
                    .selectAll("line")
                    .data(links)
                    .enter().append("line")
                    .attr("class", "link");

                // Draw nodes
                const node = svg.append("g")
                    .attr("class", "nodes")
                    .selectAll("circle")
                    .data(nodes)
                    .enter().append("circle")
                    .attr("r", 10)
                    .call(d3.drag()
                        .on("start", dragStarted)
                        .on("drag", dragged)
                        .on("end", dragEnded));

                // Add labels
                const label = svg.selectAll(null)
                    .data(nodes)
                    .enter()
                    .append("text")
                    .attr("x", 15)
                    .attr("y", ".31em")
                    .text(d => d.label);

                // Update simulation positions
                simulation.on("tick", () => {
                    link
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);

                    node
                        .attr("cx", d => d.x)
                        .attr("cy", d => d.y);

                    label
                        .attr("x", d => d.x + 10)
                        .attr("y", d => d.y);
                });

                // Drag functions
                function dragStarted(event, d) {
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                }

                function dragged(event, d) {
                    d.fx = event.x;
                    d.fy = event.y;
                }

                function dragEnded(event, d) {
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }
            });
    </script>
</body>
</html>
```

## 3. Running the App

To run this application, follow these steps:

1. Install dependencies:

    ```bash
    pip install Flask gremlinpython
    ```

2. Run the PyFlask app:

    ```bash
    python app.py
    ```

3. Open your browser and navigate to `http://localhost:5000` to see the graph visualization.

#### Python Code to Convert elementMap() to D3.js Format
```python
import json

# Sample Gremlin elementMap result
result = [
    {
        "id": 1,
        "label": "person",
        "name": "Alice",
        "age": 30,
        "outE": {
            "knows": [{"id": 101, "inV": 2, "since": 2015}]
        }
    },
    {
        "id": 2,
        "label": "person",
        "name": "Bob",
        "age": 35
    }
]

# Initialize empty node and link lists
nodes = []
links = []

# Dictionary to track already added nodes
added_nodes = set()

# Function to add nodes if not already added
def add_node(node_id, label, properties):
    if node_id not in added_nodes:
        nodes.append({
            "id": node_id,
            "label": label,
            "properties": properties
        })
        added_nodes.add(node_id)

# Parse the elementMap recursively
for element in result:
    # Add the node (vertex)
    node_id = element.get("id")
    node_label = element.get("label")
    node_properties = {k: v for k, v in element.items() if k not in ["id", "label", "outE"]}
    add_node(node_id, node_label, node_properties)

    # If the node has outgoing edges (outE)
    if "outE" in element:
        for edge_label, edges in element["outE"].items():
            for edge in edges:
                edge_id = edge.get("id")
                target_id = edge.get("inV")
                edge_properties = {k: v for k, v in edge.items() if k not in ["id", "inV"]}
                
                # Add the target node if not already added
                add_node(target_id, None, {})  # In this case, we don't know the label/properties yet
                
                # Add the edge (link)
                links.append({
                    "source": node_id,
                    "target": target_id,
                    "label": edge_label,
                    "properties": edge_properties
                })

# Create the D3.js compatible JSON structure
graph_data = {
    "nodes": nodes,
    "links": links
}

# Convert the graph data into JSON format
graph_json = json.dumps(graph_data, indent=2)

# Print or save the JSON data
print(graph_json)

# Save to a JSON file (optional)
with open('graph_data.json', 'w') as f:
    f.write(graph_json)

```