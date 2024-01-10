```html
//index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Graph Visualization</title>
    <script src="https://d3js.org/d3.v5.min.js"></script>
    <style>
        /* Add your styles here */
        .links line {
          stroke: #999;
          stroke-opacity: 0.6;
        }

        .nodes circle {
          stroke: #fff;
          stroke-width: 1.5px;
        }
    </style>
</head>
<body>
    <div id="graph"></div>
    <script src="script.js"></script>
</body>
</html>

```

```html
//script.js
<script>
    // Set the dimensions for the canvas
const width = 800, height = 600;

// Sample data - replace with your data source
const graph = {
  nodes: [
    {id: 'A'}, {id: 'B'}, {id: 'C'}, {id: 'D'}
  ],
  links: [
    {source: 'A', target: 'B'}, {source: 'A', target: 'C'}, {source: 'B', target: 'C'}, {source: 'C', target: 'D'}
  ]
};

// Create the SVG canvas
const svg = d3.select("#graph").append("svg")
    .attr("width", width)
    .attr("height", height);

// Create the simulation with forces
const simulation = d3.forceSimulation(graph.nodes)
    .force("link", d3.forceLink(graph.links).id(d => d.id))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2));

// Render the links (lines)
const link = svg.append("g")
    .attr("class", "links")
  .selectAll("line")
  .data(graph.links)
  .enter().append("line");

// Render the nodes (circles)
const node = svg.append("g")
    .attr("class", "nodes")
  .selectAll("circle")
  .data(graph.nodes)
  .enter().append("circle")
    .attr("r", 5)  // Radius of node
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

// Add event listener for node click
node.on("click", d => {
    // Handle click event
    alert("Node clicked: " + d.id);
});

// Update positions each tick
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
```

```comment
D3.js:

The script defines the dimensions of the SVG canvas and some sample data for the graph.
It creates an SVG element inside the div with the id graph.
D3.js's forceSimulation is used for positioning nodes and links.
Nodes and links are appended to the SVG as circles and lines.
Drag and click interactions are added to the nodes.
```