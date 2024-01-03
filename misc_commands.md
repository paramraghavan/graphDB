# gremlin how to list all the vertexs abd edges in tablular format

Gremlin itself doesn't inherently support a "table" structure like SQL, you would typically format the results into a table-like structure in your application code after retrieving the data. However, you can structure your query to make this post-processing as straightforward as possible.

## Listing All Vertices
```groovy
# This query will return a list of maps, where each map represents
# a vertex with its id, label, and a map of its properties (properties).
g.V().project('id', 'label', 'properties')
     .by(T.id)
     .by(T.label)
     .by(valueMap())
     .toList()

```

## Listing All Edges
```groovy

# This query will return a list of maps, where each map represents an edge with its id,
# label, outV (outgoing vertex ID), inV (incoming vertex ID), 
# and a map of its properties (properties).

g.E().project('id', 'label', 'outV', 'inV', 'properties')
     .by(T.id)
     .by(T.label)
     .by(outV().id())
     .by(inV().id())
     .by(valueMap())
     .toList()
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
g.V().drop().iterate()
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
