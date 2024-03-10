# Merge Vertex and Edge
**TinkerPop 3.6 introduced mergeV and mergeE steps** that streamline the process of adding vertices and edges only if they don't already exist. These steps simplify the previously more complex process of manually checking for the existence of elements before adding them.

## Using mergeV - Merging Vertices
The mergeV step is used to either retrieve an existing vertex that matches the provided properties or create a new vertex if no match is found.

In the following example, mergeV will search for a vertex with the label 'person' and the name 'John Doe'. If such a vertex doesn't exist, it will create a new one.
```groovy
// Example in Gremlin Console

// Add or retrieve a vertex with a unique property
vertex_label = 'person'
unique_key = 'name'
unique_value = 'John Doe'

// Using mergeV
vertex = g.V().mergeV(vertex_label).property(unique_key, unique_value).next()

```

## Using mergeE - Merging Edges
The mergeE step is used similarly to mergeV, but for edges. It either retrieves an existing edge that matches the provided criteria or creates a new edge if no match is found.

In the following example, mergeE will search for an edge with the label 'knows' from the vertex with ID source_id to the vertex with ID target_id. If such an edge doesn't exist, it will create a new one. It is assumed that both the source and target vertex's exist.  If either the source or target vertex is not found, the traversal will result in an error or exception.
```groovy
// Assuming source_vertex and target_vertex are the IDs of vertices you want to connect
source_id = 'source_vertex_id'
target_id = 'target_vertex_id'
edge_label = 'knows'

// Using mergeE
edge = g.V(source_id).mergeE(edge_label).to(V(target_id)).next()

```

## Merging Edges - what if source or target or both source and target do not exist
```python
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

# Establish a connection to the Gremlin Server
g = traversal().withRemote(DriverRemoteConnection('ws://localhost:8182/gremlin', 'g'))

# Assuming source_vertex and target_vertex are the IDs of vertices you want to connect
source_id = 'source_vertex_id'
target_id = 'target_vertex_id'
edge_label = 'knows'

# Check if both vertices exist
source_exists = g.V(source_id).hasNext()
target_exists = g.V(target_id).hasNext()

if source_exists and target_exists:
    # If both vertices exist, create or merge the edge
    edge = g.V(source_id).addE(edge_label).to(g.V(target_id)).next()
else:
    # Handle the case where one or both vertices do not exist
    print("One or both vertices not found")
```


## Load Airports
```groovy
g.V().mergeV('airport').property(T.id, 'JFK').property('name', 'John F. Kennedy International Airport').iterate()
g.V().mergeV('airport').property(T.id, 'LAX').property('name', 'Los Angeles International Airport').iterate()
// ... and so on for each airport
```

## Load Routes
```groovy
g.V('JFK').as('a').V('LAX').mergeE('route').from('a').property('distance', 3983).iterate()
g.V('LAX').as('a').V('ORD').mergeE('route').from('a').property('distance', 1744).iterate()
// ... and so on for each route

```

## g.V().mergeV('airport').property(T.id, row['code']).property('name', row['name']).next() - explain
- mergeV is a custom step used for "upsert" operations — that is, to either update an existing vertex if it matches certain criteria or create a new vertex if it doesn't exist.
- g.V(): This starts a traversal at all vertices in the graph.
- mergeV('airport'): This is a custom step that is not part of standard TinkerPop. Assuming its functionality, this step would check for the existence of an 'airport' vertex. If such a vertex exists, the traversal would continue from this vertex; if it doesn't exist, a new 'airport' vertex would be created.
- .property(T.id, row['code']): This sets the ID of the vertex. In TinkerPop, T.id is a token representing the ID of an element (vertex or edge). row['code'] would be the value from your data source (like a row in a CSV file) that you want to use as the ID of the vertex.
- .property('name', row['name']): This adds or updates a property named 'name' on the vertex, setting it to the value row['name'] from your data source.
- .next(): This step iterates the traversal and returns the next item from the result. In the context of this query, it would return the vertex that was either found or created.



## g.V().mergeV('airport').property(T.id, row['code']).property('name', row['name']).next()   using fold

- If mergeV is not available in your Gremlin implementation, you would need to use a combination of fold() and coalesce() to achieve a similar result. Here is how you can rewrite the query using these steps:
```groovy
g.V().has('airport', 'code', row['code'])
  .fold()
  .coalesce(unfold(), addV('airport').property(T.id, row['code']).property('name', row['name']))
  .next()
```
- has('airport', 'code', row['code']): Checks for an existing vertex with the label 'airport' and the specified code.
- fold(): Collects the results into a list.
- coalesce(unfold(), ...): If the list is not empty (i.e., the vertex exists), it unfolds the list, effectively selecting the existing vertex. If the list is empty (i.e., no such vertex exists), it executes the second part of the coalesce, creating a new vertex.
- addV('airport')...: Adds a new vertex with the specified properties if no vertex was found