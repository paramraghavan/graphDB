# gremlin how to list all the vertexs abd edges in tablular format

Gremlin itself doesn't inherently support a "table" structure like SQL, you would typically format the results into a table-like structure in your application code after retrieving the data. However, you can structure your query to make this post-processing as straightforward as possible.


## the double underscore __ 
In Gremlin, the double underscore __ is used as an anonymous traversal source. It's a way to start a new traversal within the context of another traversal. This is particularly useful in scenarios where you want to apply a traversal step (like valueMap()) in the middle of an ongoing traversal sequence.

Suppose you have a graph with vertices representing airports, and these vertices have properties like airport code and airport name. If you
want to retrieve these properties for each airport, you can use the valueMap() step. However, if you're already in the middle of a traversal 
(like when using project() to format your output), you need to start a new traversal for the properties. That's where __ comes in.

### Without __:
```python
g.V().valueMap('code', 'name').toList()
```

### With __:
In the following query, you're projecting each vertex into two fields: 'id' and 'details'. The id is obtained directly using T.id, but for 'details', you need to fetch both code and name. Here, __.valueMap(‘code’, ‘name’) starts a new traversal for each vertex being processed, fetching the name and age properties.
* g.V(): Starts a traversal from all vertices in the graph.
* project('id', 'details'): Formats the output into two fields, 'id' and 'details'.
* by(T.id): Fills the 'id' field with the vertex ID.
* by(__.valueMap(‘code’, ‘name’)): Fills the 'details' field. The double underscore __ starts a new traversal for each vertex to fetch its code and name properties.

```python
g.V().project('id', 'details').by(T.id).by(__.valueMap('code', 'name')).toList()

#output
# [{'id': 9664, 'details': {'code': ['LHR'], 'name': ['Heathrow Airport']}},
#  {'id': 3458,
#   'details': {'code': ['CDG'], 'name': ['Charles de Gaulle Airport']}}
# ]

```

## Listing All Vertices
```groovy
# This query will return a list of maps, where each map represents
# a vertex with its id, label, and a map of its properties (properties).
g.V().project('id', 'label', 'properties')\
      .by(T.id)\
      .by(T.label)\
      .by(__.valueMap())\
      .toList()
# Note:
# __ before valueMap() to indicate it's a step in the traversal.
```

## Listing All Edges
```groovy

# This query will return a list of maps, where each map represents an edge with its id,
# label, outV (outgoing vertex ID), inV (incoming vertex ID), 
# and a map of its properties (properties).

results = g.E().project('id', 'label', 'outV', 'inV', 'properties')\
     .by(T.id)\
     .by(T.label)\
     .by(__.outV().id())\
     .by(__.inV().id())\
     .by(__.valueMap())\
     .toList()
     
# output
#[{'id': 22016, 'label': 'route', 'outV': 3458, 'inV': 4739, 'properties': {'miles': 7459}}, 
#{'id': 29953, 'label': 'route', 'outV': 3458, 'inV': 2336, 'properties': {'miles': 6298}}]    
```

# Tablular format using python + pandas 
```python
import pandas as pd

# Assume vertices and edges are the result of the Gremlin queries above
vertices = g.V().project('id', 'label', 'properties')
edges = g.E().project('id', 'label', 'outV', 'inV', 'properties')

# Convert to DataFrames
vertices_df = pd.DataFrame(vertices)
edges_df = pd.DataFrame(edges)

# Now you can display these DataFrames as tables
print(vertices_df)
print(edges_df)

```

## query all vertices with a certain label and their outgoing edges with certain labels in a Gremlin graph
```groovy
g.V().hasLabel('vertexLabel').outE('edgeLabel')

# query and print the vertices and edges
g.V().hasLabel('vertexLabel').outE('edgeLabel').project('vertex', 'edge')
  .by(inV().values('propertyName').fold())
  .by(valueMap())

```

## Cleanup
Delete all vertices and edges in a TinkerPop-enabled graph database using Gremlin, you can use a straightforward Gremlin query. 

```groovy
# g.V(): Retrieves all vertices in the graph.
# .drop(): Marks each vertex for deletion.
# .iterate(): Executes the operation.
g.V().limit(10000).drop().iterate()
```

- clean up using curl command
```
curl -X POST --data-urlencode "update=DELETE WHERE { ?s ?p ?o }" http://your-neptune-endpoint:8182/sparql
OR
curl -X POST -d '{"gremlin":"g.V().drop().iterate()"}' http://your-neptune-endpoint:8182/gremlin
```

## distict labels
- g.V().label().dedup()
- g.E().label().dedup()
- g.E().label().dedup().count()


## Backup Graph
3 steps
- Query the Graph Database: Use Gremlin queries to retrieve all vertices and edges.
```
For vertices: 
g.V().valueMap().with(WithOptions.tokens).toList()
For edges:
 g.E().project('id', 'label', 'outV', 'inV', 'properties').by(T.id).by(T.label).by(outV().id()).by(inV().id()).by(valueMap()).toList()
```
- Serialize the Data: Convert the data to a suitable format, such as JSON.
- Save to a File: Write the serialized data to a file.
```python
import json
from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

# Initialize Gremlin Graph
graph = Graph()

# Connect to the Gremlin Server
remoteConn = DriverRemoteConnection('ws://localhost:8182/gremlin','g')
g = graph.traversal().withRemote(remoteConn)

# Fetch vertices and edges
vertices = g.V().valueMap().with_(WithOptions.tokens).toList()
edges = g.E().project('id', 'label', 'outV', 'inV', 'properties').by(T.id).by(T.label).by(__.outV().id()).by(__.inV().id()).by(__.valueMap()).toList()

# Close the connection
remoteConn.close()

# Serialize data to JSON
vertices_json = json.dumps(vertices)
edges_json = json.dumps(edges)

# Write data to files
with open('vertices_backup.json', 'w') as f:
    f.write(vertices_json)

with open('edges_backup.json', 'w') as f:
    f.write(edges_json)

print("Backup completed.")

```


## Backup and Restore Graph

### Backup to file
```python
from gremlin_python import statics
from gremlin_python.structure.io.graphsonV3d0 import GraphSONReader, GraphSONWriter
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

# Connect to the graph
g = traversal().withRemote(DriverRemoteConnection('ws://localhost:8182/gremlin','g'))

# Extract all vertices and edges
vertices = g.V().valueMap().with_(statics.include, statics.T.id).toList()
edges = g.E().valueMap().with_(statics.include, statics.T.id, statics.T.label).toList()

# Save to a file
with open("backup_vertices.json", "w") as f:
    GraphSONWriter().writeObject(f, vertices)

with open("backup_edges.json", "w") as f:
    GraphSONWriter().writeObject(f, edges)

```

### Restore the Graph from the Backup File
```python
from gremlin_python import statics
from gremlin_python.structure.io.graphsonV3d0 import GraphSONReader, GraphSONWriter
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

# Connect to the graph
g = traversal().withRemote(DriverRemoteConnection('ws://localhost:8182/gremlin','g'))

# Assuming the same imports and graph connection as above

# Read the data from the backup files
with open("backup_vertices.json", "r") as f:
    vertices_data = GraphSONReader().readObject(f)

with open("backup_edges.json", "r") as f:
    edges_data = GraphSONReader().readObject(f)

# Create vertices
for v in vertices_data:
    properties = {k: v[k][0] for k in v if k != 'id'}  # Assuming single properties
    g.addV().property('id', v['id']).propertyMap(properties).next()

# Create edges
for e in edges_data:
    properties = {k: e[k][0] for k in e if k not in ['id', 'label']}
    g.addE(e['label']).from_(g.V(e['outV'])).to(g.V(e['inV'])).propertyMap(properties).next()
```

## All Routes Between Two Given Airports
Let's assume the airports are represented as vertices in your graph and routes as edges. If each airport has a unique identifier (like an airport code), you can use them to specify the source and target airports. Here's a generic Gremlin query to find all routes between two airports, identified by airport1 and airport2:
```groovy
g.V().has('airport', 'code', 'airport1')
  .repeat(bothE().otherV())
  .until(has('airport', 'code', 'airport2'))
  .path()
  .toList()
# b/w jfk and LAX
g.V().has('airport', 'code', 'JFK').\
repeat(out().simplePath()).\
until(has('airport', 'code', 'LAX'))\
.path()\
.by('code')
```

## All Routes In and Out of an Airport

```groovy
g.V().has('airport', 'code', 'airportCode')
  .bothE()
  .project('route', 'from', 'to')
  .by('id')
  .by(outV().values('code'))
  .by(inV().values('code'))
  .toList()

```

- Incoming routes
```groovy
g.V().has('airport', 'code', 'JFK').inE().outV().path().by('code')
```
- Outgoing routes
```groovy
g.V().has('airport', 'code', 'JFK').outE().inV().path().by('code')
```

## Query all airports downstream to an airport for example JFK
```groovy
g.V().has('airport', 'code', 'JFK') // start at the JFK airport vertex
  .repeat(out()) // repeat traversal from each vertex to its outgoing vertices
  .emit() // include all visited vertices in the results
  .dedup() // remove duplicates
  .values('code') // extract the airport codes of the downstream airports
  .toList() // collect the results into a list
```
- has('airport', 'code', 'JFK'): Filters vertices to find the one that represents JFK airport.
- repeat(out()): Repeats the traversal from each airport to the airports it has routes to. This follows the direction of the edges, effectively finding downstream airports.
- emit(): Outputs the airports at each step of the traversal.
- dedup(): Removes any duplicate airports that might be reached through different routes.
- values('code'): Gets the 'code' property of the airport vertices, which represents the airport codes.
- toList(): Collects all the results into a list.
> If you want to limit the depth of the traversal to, for example, only airports that can be reached with one connecting flight, 
> you can add a times(n) step after repeat where n is the number of allowed "hops".

## All airpots upstream to MIA
```groovy
g.V().has('airport', 'code', 'MIA') // start at the Miami airport vertex
  .repeat(in()) // repeat traversal from each vertex to its incoming vertices
  .emit() // include all visited vertices in the results
  .dedup() // remove duplicates
  .values('code') // extract the airport codes of the upstream airports
  .toList() // collect the results into a list
```
- has('airport', 'code', 'MIA'): This step finds the vertex that represents Miami Airport, assuming that 'airport' is the label of airport vertices and 'code' is the property that stores the airport code.
- repeat(in()): This step repeatedly traverses from each airport to the airports that have a route to it. The in() step specifically follows incoming edges to the current vertex, which corresponds to routes from other airports to the current one.
- emit(): This step ensures that all vertices visited during the traversal are included in the results.
- dedup(): This step is used to remove any duplicate vertices that may have been visited more than once during the traversal.
- values('code'): This step retrieves the values of the 'code' property, which should be the airport codes.
- toList(): This step collects all the airport codes into a list which will be the output of the query.

>Replace 'airport' and 'code' with the actual label and property names used in your graph. If you want to limit the traversal to a 
>certain number of hops (e.g., only direct flights to Miami), you can modify the query to include a times(n) step after repeat,
> where n is the number of hops you want to allow
> 
 
## tree
```markdown
Get all the path from root to leaves which has at least one of the vertex from a vertexList, vertexList = [2,3,5,6]

g.V(1).repeat(out()).until(outE().count().is(0)).path().
  filter(unfold().is(within(vertexList)))


Get all such paths, where path contains at least half of the vertices from vertexList.

g.V(1).repeat(out()).until(outE().count().is(0)).path().
  filter(unfold().is(within(vertexList)).count().is(gte(vertexList.size() / 2))


g.V().has('Entity', 'name', 'sourceEntityName') // Start at the source entity
  .repeat(out('childOf')) // Traverse through 'childOf' relationships
  .until(has('Entity', 'name', 'targetEntityName')) // Continue until the target entity is reached
  .path() // Collect the path from source to target
  .toList() // Output the result as a list

g.V().has('Entity', 'name', 'sourceEntityName'): Starts the traversal at the vertex representing the source entity.
.repeat(out('childOf')): Repeatedly follows the childOf edges to downstream entities.
.until(has('Entity', 'name', 'targetEntityName')): Continues the traversal until it finds the target entity.
.path(): Collects the entire path of the traversal from the source to the target.
.toList(): Converts the result to a list for output.
```