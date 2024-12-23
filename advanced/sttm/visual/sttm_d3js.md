```text
Read csv file with columns source, target.
source and target are table names
Use d3.js to read this csv file and create a graph  using the above csv file
Ability to filter graph by source to target moving from left to right with swim lanes, clicking on the  node highlight the path
```
## Source
```html
<!DOCTYPE html>
<html>
<head>
    <title>D3 Graph Visualization</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <style>
        .node {
            fill: #69b3a2;
            stroke: #fff;
            stroke-width: 2px;
        }
        
        .link {
            stroke: #999;
            stroke-opacity: 0.6;
            stroke-width: 2px;
        }
        
        .node text {
            font-size: 12px;
            font-family: sans-serif;
        }
        
        .highlighted {
            stroke: #ff0000;
            stroke-width: 3px;
        }
        
        .node.highlighted {
            fill: #ff7f50;
        }
        
        #controls {
            margin: 20px;
        }
    </style>
</head>
<body>
    <div id="controls">
        <label for="sourceFilter">Filter by Source:</label>
        <select id="sourceFilter"></select>
    </div>
    <svg id="graph"></svg>

    <script>
        // Sample CSV data
        const csvData = `source,target
customers,orders
orders,order_items
customers,customer_addresses
order_items,products
products,categories
orders,shipments
shipments,shipping_methods`;

        // Parse CSV
        const data = d3.csvParse(csvData);

        // Set up the SVG
        const width = 800;
        const height = 600;
        const margin = { top: 20, right: 20, bottom: 20, left: 20 };

        const svg = d3.select("#graph")
            .attr("width", width)
            .attr("height", height);

        // Create a map of nodes and their levels
        const nodes = new Set();
        data.forEach(d => {
            nodes.add(d.source);
            nodes.add(d.target);
        });

        // Convert to array and calculate levels
        const nodeArray = Array.from(nodes).map(id => ({ id }));
        const links = data.map(d => ({
            source: d.source,
            target: d.target
        }));

        // Calculate node levels (x-positions)
        const levels = {};
        const visited = new Set();

        function calculateLevels(node, level = 0) {
            if (!visited.has(node)) {
                visited.add(node);
                levels[node] = Math.max(level, levels[node] || 0);
                
                links.forEach(link => {
                    if (link.source === node) {
                        calculateLevels(link.target, level + 1);
                    }
                });
            }
        }

        // Find root nodes (nodes with no incoming edges)
        const rootNodes = new Set(nodes);
        links.forEach(link => rootNodes.delete(link.target));
        rootNodes.forEach(node => calculateLevels(node));

        // Update node positions based on levels
        nodeArray.forEach(node => {
            node.x = (levels[node.id] * width) / (Math.max(...Object.values(levels)) + 1) + 100;
            node.y = height / 2;
        });

        // Create the force simulation
        const simulation = d3.forceSimulation(nodeArray)
            .force("link", d3.forceLink(links).id(d => d.id).distance(150))
            .force("charge", d3.forceManyBody().strength(-1000))
            .force("x", d3.forceX().x(d => d.x).strength(0.5))
            .force("y", d3.forceY().y(d => d.y).strength(0.1));

        // Create links
        const link = svg.append("g")
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("class", "link");

        // Create nodes
        const node = svg.append("g")
            .selectAll("g")
            .data(nodeArray)
            .join("g")
            .attr("class", "node-group");

        node.append("circle")
            .attr("class", "node")
            .attr("r", 20);

        node.append("text")
            .text(d => d.id)
            .attr("text-anchor", "middle")
            .attr("dy", 30);

        // Add drag behavior
        node.call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

        // Populate source filter dropdown
        const sourceFilter = document.getElementById("sourceFilter");
        const uniqueSources = [...new Set(data.map(d => d.source))];
        sourceFilter.innerHTML = '<option value="">All</option>' + 
            uniqueSources.map(source => 
                `<option value="${source}">${source}</option>`
            ).join('');

        // Filter function
        sourceFilter.addEventListener('change', function() {
            const selectedSource = this.value;
            
            if (selectedSource) {
                const relevantLinks = links.filter(l => l.source.id === selectedSource || l.target.id === selectedSource);
                const relevantNodes = new Set();
                relevantLinks.forEach(l => {
                    relevantNodes.add(l.source.id);
                    relevantNodes.add(l.target.id);
                });

                node.style("opacity", d => relevantNodes.has(d.id) ? 1 : 0.2);
                link.style("opacity", l => 
                    relevantNodes.has(l.source.id) && relevantNodes.has(l.target.id) ? 1 : 0.2
                );
            } else {
                node.style("opacity", 1);
                link.style("opacity", 1);
            }
        });

        // Highlight paths on node click
        node.on("click", function(event, d) {
            // Reset all highlights
            node.selectAll("circle").classed("highlighted", false);
            link.classed("highlighted", false);

            // Find all connected paths
            const paths = findPaths(d.id);
            paths.forEach(path => {
                // Highlight nodes in path
                node.filter(n => path.includes(n.id))
                    .selectAll("circle")
                    .classed("highlighted", true);

                // Highlight links in path
                path.forEach((node, i) => {
                    if (i < path.length - 1) {
                        link.filter(l => 
                            l.source.id === path[i] && l.target.id === path[i + 1]
                        ).classed("highlighted", true);
                    }
                });
            });
        });

        // Function to find all paths from a node
        function findPaths(startNode, visited = new Set(), path = []) {
            const paths = [];
            path.push(startNode);
            visited.add(startNode);

            const outgoingLinks = links.filter(l => l.source.id === startNode);
            if (outgoingLinks.length === 0) {
                paths.push([...path]);
            } else {
                outgoingLinks.forEach(link => {
                    if (!visited.has(link.target.id)) {
                        paths.push(...findPaths(link.target.id, new Set(visited), [...path]));
                    }
                });
            }

            return paths;
        }

        // Simulation tick function
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node.attr("transform", d => `translate(${d.x},${d.y})`);
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
    </script>
</body>
</html>
```
