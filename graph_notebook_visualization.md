# Graph noteboo  Viusalization

>Ref: https://docs.aws.amazon.com/neptune/latest/userguide/notebooks-visualization.html

## Generic gremlin query to be used for visualizing the graph
Creating a generic Gremlin query for visualizing a graph depends on various factors, including the specific graph database you're using, 
the visualization tools available, and your requirements. However, I can provide you with a basic template for a Gremlin query that you can 
adapt and enhance for your needs.

You can then take the extracted data and use it with a visualization library or tool of your choice (e.g., GraphViz, D3.js, or Gephi) to 
create visual representations of the graph.

```gremlin
// Start the traversal from a specific vertex or with a specific condition
g.V().has('property', 'value')
  .outE()  // Traverse outgoing edges
  .inV()   // Traverse to neighboring vertices
  .project('source', 'target', 'edgeProperty')  // Extract relevant data for visualization
    .by(id())          // Extract the ID of the source vertex
    .by(inV().id())    // Extract the ID of the target vertex
    .by('property')    // Extract properties of the edge
  .toList()
```

```gremlin
g.V().outE().inV().project('source', 'target', 'edgeProperty').by(id()).by(out().id()).by('property').path()

g.V().outE().inV().path()
```

## Generic gremlin query to pull all the nodes and edges with  depth limit
Following query will return paths representing the traversals up to the specified depth. Each path is a sequence of
vertices and edges. 
>Note: that this query could potentially return a large amount of data, especially in dense
> graphs or with a high depth limit, so it's important to use such queries cautiously in production environments.

```gremlin
g.V() // Start from all vertices in the graph
  .repeat(bothE().otherV().simplePath()) // Traverse both in and out edges, ensuring simple paths
    .times(depthLimit) // Repeat traversal up to the depth limit
  .path() // Generate paths representing traversals
  .toList() // Collect the results into a list
```
* g.V(): Start the traversal from all vertices in the graph.
* repeat(bothE().otherV().simplePath()): This repeats the traversal pattern within its parentheses. The bothE() step
  fetches both incoming and outgoing edges from the current vertex, otherV() moves the traversal to the vertex at the
  other end of each edge, and simplePath() ensures that the traversal does not revisit any vertices, preventing cycles
  in the path.
* .times(depthLimit): This specifies how many times to repeat the traversal, effectively setting the depth limit.
* .path(): Generates the paths taken during the traversal. Each path includes the vertices and edges traversed.
* .toList(): Collects the results into a list for further processing or examination


## Visualizing Gremlin query results

Neptune workbench creates a visualization of the query results for any Gremlin query that returns a path. To see the visualization, 
select the Graph tab to the right of the Console tab under the query after you run it.

You can use query visualization hints to control how the visualizer diagrams query output. These hints follow the %%gremlin cell magic 
and are preceded by the --path-pattern (or its short form, -p) parameter name:

```gremlin
%%gremlin -p comma-separated hints
```

```gremlin
%%gremlin -p v,oute,inv
g.V().outE().inV().path().by(valueMap('code', 'name')).order(local).by(keys)

%%gremlin -p v,oute,inv
g.V().outE().inV().path().by(valueMap('miles','code', 'name')).order(local).by(keys)

```