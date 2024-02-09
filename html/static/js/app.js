document.getElementById('queryForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const query = document.getElementById('queryInput').value;
    fetch('/query', {
        method: 'POST',
        body: new URLSearchParams('query=' + query)
    })
    .then (
        response => response.json()
     )
    .then(data => {
        load(data.nodes, data.edges)
    })
    .catch(error => console.error('Error:', error));
});

function load(nodes, links) {
        const svg = d3.select("svg"),
            width = +svg.attr("width"),
            height = +svg.attr("height");

        const color = d3.scaleOrdinal(d3.schemeCategory10);

        // Define the force simulation
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id))
            .force("charge", d3.forceManyBody())
            .force("center", d3.forceCenter(width / 2, height / 2));

        // Tooltip setup
        const tooltip = d3.select(".tooltip");

        // Draw links (lines)
        const link = svg.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(links)
            .enter().append("line")
            .attr("class", "link")
            .style("stroke-width", d => d.width || 2)
            .on("mouseover", function(event, d) {
                tooltip.transition()
                    .duration(200)
                    .style("opacity", .9);
                tooltip.html(d.miles)
                    .style("left", (event.pageX) + "px")
                    .style("top", (event.pageY - 28) + "px");
            })
            .on("mouseout", function(d) {
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
            }); // Example to set link width

        // Draw nodes (circles)
        const node = svg.append("g")
            .attr("class", "nodes")
            .selectAll("circle")
            .data(nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", 15) // Radius of node
            .style("fill", d => color(d.color)) // Color nodes based on grouping
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended))
            .on("mouseover", function(event, d) {
                tooltip.transition()
                    .duration(200)
                    .style("opacity", .9);
                tooltip.html(d.code + "<br/>" +  d.color)
                    .style("left", (event.pageX) + "px")
                    .style("top", (event.pageY - 28) + "px");
            })
            .on("mouseout", function(d) {
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
            });

        var labels = svg.append("g")
          .attr("class", "labels")
          .selectAll("text")
          .data(nodes)
          .enter().append("text")
            .text(d => d.code)
            .attr("x", 8)
            .attr("y", "0.31em");

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
            labels
                .attr("x", d => d.x + 10)
                .attr("y", d => d.y);
        });
        // Assuming you have the force simulation set up as in the previous example

        // Set a constant distance for all links
        simulation.force("link").distance(300);

        // Alternatively, set dynamic distances based on link properties
        //simulation.force("link").distance(d => d.desiredLength);

        // Restart the simulation for the changes to take effect
        //simulation.alpha(1).restart();

        // Update the thickness of a specific edge
<!--        svg.selectAll("line")-->
<!--            .filter(d => d.id === "specificEdgeId") // Filter to the specific edge you want to update-->
<!--            .style("stroke-width", newThickness); // Set new thickness-->

        // Drag functions
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            if (event.subject && event.subject.x)
                event.subject.fx = event.subject.x;
            if (event.subject && event.subject.y)
            event.subject.fy = event.subject.y;
        }

        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            if (event.subject && event.subject.fx)
            event.subject.fx = null;
            if (event.subject && event.subject.fy)
            event.subject.fy = null;
        }

}


