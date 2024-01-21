# Querying a lineage graph
Querying a lineage graph from a source node to leaf nodes in Gremlin involves traversing the graph downstream from the source,
 following the edges that represent the lineage relationships.


## Writing the Gremlin Query
* Identify the Source Node: Start the traversal from a specific source node. This node could be identified by a unique property such as a
name, ID, or label. For example, if your source node has a label 'data_source' and a name property, you might start with something
like g.V().has('data_source', 'name', 'sourceName').
* Traverse the Lineage: Use a Gremlin traversal that follows the edges representing the lineage relationships. If the edges
 from parent to child are labeled 'child_of', the traversal would look like out('child_of').
* Repeat and Emit: Use repeat() to continuously traverse from each node to its children and emit() to output all nodes at
each level of the traversal.
* Limit the Traversal: Optionally, you can limit the depth of the traversal with times(n) if you want to stop
after a certain number of levels.

```
g.V().has('data_source', 'name', 'sourceName')
  .repeat(out('child_of')).emit()
  .path()
  .toList()
```

* out(): Traverses all outgoing edges from each vertex. This replaces out('child_of') and acts as a wildcard, traversing edges of any label.
* repeat(out()).emit(): Continuously repeats the traversal for all outgoing edges and emits vertices at each step.
```
g.V().has('data_source', 'name', 'sourceName')
  .repeat(out()).emit()
  .path()
  .toList()
```

* Graph list all the downstreams from vertex,  limit to depth n
```groovy
g.V(startVertexId) // Start from a specific vertex
  .repeat(out())   // Repeat traversing downstream
    .times(n)      // Limit the depth to n
  .dedup()         // Remove duplicate vertices
  .toList()        // Collect the results into a list

```

* Graph list all the downstreams vertices and edgesfrom vertex,  limit to depth n
```gremlin
g.V(startVertexId) // start from a specific vertex
  .repeat(outE().inV()) // repeat traversing from vertex to outgoing edges to their in-vertices
    .times(n) // do this for n levels deep
  .path() // collect the paths traversed
  .toList() // convert the result to a list
```

* List both vertices and edges together

```gremlin
// For vertices
g.V()

// For edges
g.E()

/ For both vertices and edges
g.V().bothE()
```