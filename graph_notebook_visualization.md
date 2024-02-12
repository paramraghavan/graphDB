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
g.V().has('property name', 'its value')
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
// g.V().group().by(label).by(count())
// g.V().repeat(out()).times(3).path()
// g.V().repeat(out()).times(3).path().by(elementMap())
// g.V().hasLabel('airport').repeat(outE().inV()).times(2).path().by(elementMap())
// g.V().outE().inV().path().by(elementMap())
// g.V().repeat(out()).times(3)
// g.V().outE().inV().path().by(valueMap())
// g.V().repeat(outE().inV()).times(2).path().by(valueMap())
// g.V().repeat(outE().inV()).times(2).path().by(valueMap()).toList()
// g.V().repeat(bothE().otherV()).times(2).path().by(__.elementMap()).toList()
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

## Gremlin query returning a tree structure of vertices and edges
Following example assumes you are working with a graph that has vertices connected by edges, you want to build a tree starting from a specific vertex
```gremlin
g.V().has('airport::vertex', 'code', 'LAX').repeat(out()).times(2).emit().tree().by('code')
g.V().has('airport::vertex', 'code', 'LAX').repeat(out()).times(2).emit().tree().path().by(elementMap())
g.V(startVertexId) // Start from a specific vertex
  .repeat(out()simplePath())    // Recursively traverse outgoing edges, Use simplePath to avoid cycles
  .emit()           // Emit all vertices encountered during the traversal
  .tree()           // Construct a tree structure from the traversal
  .by('name')       // Optionally, label the tree nodes using the 'name' property of each vertex
g.V().hasLabel('airport::vertex').outE().inV().tree().by('name')
```
* g.V(startVertexId): This initiates the traversal starting from a vertex with the given ID.
* repeat(out()): This step repeats the traversal for outgoing edges from each vertex. It's the mechanism by which you
  traverse the graph.
* emit(): This step ensures that all vertices encountered during the traversal are included in the result.
* tree(): This collects the traversal into a tree structure. The vertices are organized according to their paths in the
  traversal, effectively creating a tree representation of the graph from the starting vertex.
* by('name'): This is a modulator for the tree step, specifying that the vertices in the tree should be labeled by their
  name property. You can adjust this to use any property relevant to your graph.
