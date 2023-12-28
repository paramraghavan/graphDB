# User-supplied IDs

## Neptune
User-supplied IDs are allowed in Neptune Gremlin with the following stipulations.
- Supplied IDs are optional.
- Only vertexes and edges are supported.
- Only type String is supported.

To create a new vertex with a custom ID, use the property step with the id keyword: g.addV().property(id, 'customid').
> In the above line, do not put quotation marks around the id keyword. It refers to T.id.

All vertex IDs must be unique, and all edge IDs must be unique. However, Neptune does allow a vertex and an edge to have the same ID.

If you try to create a new vertex using the g.addV() and a vertex with that ID already exists, the operation fails. The exception to this is if you specify a new label for the vertex, the operation succeeds but adds the new label and any additional properties specified to the existing vertex. Nothing is overwritten. A new vertex is not created. The vertex ID does not change and remains unique.

```groovy
gremlin> g.addV('label1').property(id, 'customid')
gremlin> g.addV('label2').property(id, 'customid')
gremlin> g.V('customid').label()
==>label1::label2
```

### Labels
Neptune supports multiple labels for a vertex. When you create a label, you can specify multiple labels by separating them with ::. For example, g.addV("Label1::Label2::Label3") adds a vertex with three different labels. The hasLabel step matches this vertex with any of those three labels: hasLabel("Label1"), hasLabel("Label2"), and hasLabel("Label3").


## Tinkerpop
**Creating the Vertex with a UUID**
- pip install gremlinpython uuid
```python
import uuid
from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import T

# Generate a UUID
vertex_id = str(uuid.uuid4())

# Connection setup for your graph database
# Replace 'ws://localhost:8182/gremlin' with your Gremlin Server URL
graph = Graph()
g = graph.traversal().withRemote(DriverRemoteConnection('ws://localhost:8182/gremlin', 'g'))

# Add a vertex with a custom UUID
g.addV('vertexLabel').property(T.id, vertex_id).next()


# query by user defined id
# Query the vertex by the custom UUID
queried_vertex = g.V(vertex_id).toList()
# Display the result
print(queried_vertex)

# Close the connection
g.close()
```


## Datatype supported for Vertex and edge id's
In Apache TinkerPop, the ability to use a number or string datatype for the vertex ID depends on the underlying graph database you are using with TinkerPop.
TinkerPop itself is a graph computing framework that provides a standard way to interact with various graph databases, but it doesn't enforce specific data types for vertex IDs. This flexibility means the actual data types allowed for vertex IDs, including whether you can use a string, is determined by the specific graph database implementation.

Inmemory TinkerGraph, you can use Long data type as an identifier for a vertex and edge
```groovy
g.addV('vertexLabel').property(id, 123).next()
# Query vertx by id
g.V(123).next()
```

> **Note**: that not all TinkerPop-enabled graph databases  support Integer and 
> String data type as vertex id. For exampe Neptune only support String data type as id

- Some graphs don't allow setting the ID, you have to  set custom property - use number or String data type and use it as id, see example below:
  - Creating a Vertex with a Custom Integer ID Property:
  ```groovy
  g.addV('vertexLabel').property('myCustomId', 123).next()
  
  # Following query finds the vertex with the label 'vertexLabel'
  # and a custom property 'myCustomId' with the value 123.
  g.V().has('vertexLabel', 'myCustomId', 123).next()

  ```