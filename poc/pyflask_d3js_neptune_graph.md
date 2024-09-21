
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
nodes = []
edges = []

def parse_element_map(element_map, depth=0):
    if isinstance(element_map, list):
        for item in element_map:
            parse_element_map(item, depth + 1)
    elif isinstance(element_map, dict):
        node = {}
        edge = {}
        for key, value in element_map.items():
            if key == "outE":
                for edge_label, edge_list in value.items():
                    for edge_item in edge_list:
                        source_id = element_map.get("id")
                        target_id = edge_item['inV'].get('id')
                        edges.append({
                            'source': source_id,
                            'target': target_id,
                            'label': edge_item.get('label'),
                            'properties': {k: v for k, v in edge_item.items() if k not in ['id', 'label', 'inV']}
                        })
                        # Recursively parse target node
                        parse_element_map(edge_item['inV'], depth + 1)
            elif key == 'id' or key == 'label':
                node[key] = value
            else:
                node[key] = value
        if node:
            nodes.append(node)

# Parse the result
parse_element_map(result)

# Now you have separate nodes and edges lists
print("Nodes:", nodes)
print("Edges:", edges)

```