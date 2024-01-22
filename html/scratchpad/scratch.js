// Sample data
const nodes = [
    { id: 1, label: 'Node 1', group: 1 },
    { id: 2, label: 'Node 2', group: 1 },
    { id: 3, label: 'Node 3', group: 2 }
    // ... other nodes
];

const links = [
    { source: 1, target: 2 },
    { source: 2, target: 3 }
    // ... other links
];

const svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height");

// Define the force simulation
const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2));

// Draw links (lines)
const link = svg.append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(links)
    .enter().append("line")
    .attr("class", "link");

// Draw nodes (circles)
const node = svg.append("g")
    .attr("class", "nodes")
    .selectAll("circle")
    .data(nodes)
    .enter().append("circle")
    .attr("class", "node")
    .attr("r", 5) // Radius of node
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

// Add labels to nodes
node.append("title")
    .text(d => d.label);

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
function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
}

function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
}

function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
}
