
# Rendering Neptune Nodes and Edges as JSON for D3.js using PyFlask

## Steps:

1. **Query Neptune for Nodes and Edges**  
   You'll need to query Neptune using Gremlin (or SPARQL, depending on your data model) and format the result into a JSON structure that D3.js can understand (e.g., a structure with nodes and links).

2. **Set up a Flask API to Serve the Data**  
   Use Flask to create a Python server that returns the data from Neptune in JSON format.

3. **Create an HTML Page with D3.js Visualization**  
   Render the JSON data on the front-end using D3.js for graph visualization.

## Step 1: Query Neptune and Prepare JSON Data

Use the `gremlinpython` library to query Neptune for nodes and edges, and then format the response into a D3.js compatible JSON structure.

```python
from gremlin_python.driver import client
from flask import Flask, jsonify, render_template

# Initialize the Flask app
app = Flask(__name__)

# Neptune client configuration
neptune_endpoint = 'wss://your-neptune-endpoint:8182/gremlin'
neptune_client = client.Client(neptune_endpoint, 'g')

# Gremlin query to retrieve nodes and edges
query = """
g.V().as('nodes').select('nodes').by('id').
  addE('connects').from('nodes').to(g.V().has('id', 'connected_node_id')).as('edges').
  select('edges').by(valueMap())
"""

@app.route('/graph-data', methods=['GET'])
def get_graph_data():
    # Submit the query to Neptune
    result = neptune_client.submit(query).all()

    nodes = []
    links = []

    # Convert the Neptune result to D3.js compatible format
    for item in result:
        if 'V' in item:
            # Vertex data (nodes)
            nodes.append({
                'id': item['id'],
                'label': item['label'],
                'properties': item['properties']
            })
        elif 'E' in item:
            # Edge data (links)
            links.append({
                'source': item['outV'],
                'target': item['inV'],
                'label': item['label']
            })

    # Create a dictionary for the final JSON format
    graph_data = {
        'nodes': nodes,
        'links': links
    }

    return jsonify(graph_data)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
```

In this code:
- The Gremlin query is used to get nodes and edges from Neptune.
- The result is formatted into a JSON structure with `nodes` and `links` (which are D3.js terminologies).
- `nodes` is a list of node objects, each containing an `id` and optional properties.
- `links` is a list of edges connecting the nodes, with `source` and `target` as node IDs.

## Step 2: Set Up Flask to Serve the HTML Page with D3.js

Create an HTML page that fetches the JSON data from the `/graph-data` endpoint and visualizes it using D3.js. Place this in a `templates` folder under the name `graph.html`.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D3.js Graph</title>
    <script src="https://d3js.org/d3.v6.min.js"></script>
    <style>
        .node {
            stroke: #000;
            stroke-width: 1.5px;
        }
        .link {
            stroke: #999;
            stroke-opacity: 0.6;
        }
    </style>
</head>
<body>
    <h2>D3.js Graph from Neptune</h2>
    <svg width="960" height="600"></svg>

    <script>
        // Fetch graph data from the Flask API
        fetch('/graph-data')
            .then(response => response.json())
            .then(data => {
                const width = 960;
                const height = 600;

                // Create SVG container
                const svg = d3.select("svg")
                    .attr("width", width)
                    .attr("height", height);

                // Set up the force simulation
                const simulation = d3.forceSimulation(data.nodes)
                    .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
                    .force("charge", d3.forceManyBody().strength(-200))
                    .force("center", d3.forceCenter(width / 2, height / 2));

                // Draw the links
                const link = svg.append("g")
                    .attr("class", "links")
                    .selectAll("line")
                    .data(data.links)
                    .enter().append("line")
                    .attr("class", "link");

                // Draw the nodes
                const node = svg.append("g")
                    .attr("class", "nodes")
                    .selectAll("circle")
                    .data(data.nodes)
                    .enter().append("circle")
                    .attr("class", "node")
                    .attr("r", 10)
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended));

                // Add labels
                node.append("title")
                    .text(d => d.id);

                // Update the simulation on each tick
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

                // Drag functions
                function dragstarted(event, d) {
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                }

                function dragged(event, d) {
                    d.fx = event.x;
                    d.fy = event.y;
                }

                function dragended(event, d) {
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }
            });
    </script>
</body>
</html>
```

## Step 3: Start the Flask Server

Ensure your Flask server is running so you can access the graph at `http://localhost:5000/graph`.

```bash
flask run
```

This will:
- Query Neptune for nodes and edges.
- Serve the data as JSON through the Flask endpoint `/graph-data`.
- Render the graph on an HTML page using D3.js.

### Explanation of D3.js Code:
- **D3 Simulation**: This creates a force-directed graph where nodes repel each other and links attract them.
- **Fetching Data**: The `/graph-data` endpoint is queried, and D3 renders the graph based on the returned JSON structure.
- **SVG**: D3 uses SVG to draw the graph. Nodes are circles, and links are lines.

This approach ties together Amazon Neptune, Flask, and D3.js to visualize graph data in a web application.
