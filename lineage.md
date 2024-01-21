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

// Retrieve all edges both IN and OUT
g.V().bothE()
```

* retrieve vertices along with their edges and the nature of their relationships`
```gremlin
g.V().as('vertex').bothE().as('edge').bothV().as('related_vertex').select('vertex', 'edge', 'related_vertex').dedup()
```

- g.V(): This starts the traversal at all vertices in the graph.
- as('vertex'): This step labels the current step (the vertices) for later reference.
- bothE(): This extends the traversal to the edges connected to these vertices. It includes both incoming and outgoing edges.
- as('edge'): This labels the edges for later reference.
- bothV(): This step extends the traversal from the edge to both vertices that the edge connects (it effectively gets the vertex on the other end of the edge).
- as('related_vertex'): This labels the vertices connected by the edge.
- select('vertex', 'edge', 'related_vertex'): Finally, this step selects the vertices, edges, and related vertices, essentially creating 
a map of each vertex, its connected edges, and the vertices on the other end of those edges.

* **how to limit the depth** for g.V().as('vertex').bothE().as('edge').bothV().as('related_vertex').select('vertex', 'edge', 'related_vertex')
```shell
g.V().as('vertex')
  .repeat(bothE().as('edge').bothV().as('related_vertex'))
  .times(2)
  .select('vertex', 'edge', 'related_vertex')
```
- repeat(bothE().as('edge').bothV().as('related_vertex')): This part of the query is repeated.
- times(2): This limits the repetition to 2 times, effectively setting your depth to 2.

* gremlin traverse the path and list all the vertices and edges and limit by depth d,   2

```groovy
g.V().repeat(bothE().otherV()).times(d).path().by(elementMap())

- g.V(): Starts the traversal from all vertices in the graph.
- repeat(bothE().otherV()): Repeats the pattern of traversing both edges (bothE()) and the adjacent vertices (otherV()).
- times(d): Specifies the depth of the traversal. Replace d with the desired depth limit.
- path(): Collects the paths traversed.
- by(elementMap()): Maps each element (vertex or edge) in the path to a map of its properties.

```