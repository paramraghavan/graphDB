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
- Generate the UUID: Generate a UUID in your application code. For example, in Java, you can use UUID.randomUUID().
- Create the Vertex: Use the generated UUID when creating a vertex. In some graph databases that are TinkerPop-enabled, you can directly set the ID of a vertex (if the database configuration allows it). Here's how you might do it:
```groovy
import java.util.UUID;

# In this example:
# T.id is a TinkerPop token for specifying the ID.
# uuid is the UUID generated.
# 'vertexLabel' is your custom label for the vertex.

UUID uuid = UUID.randomUUID();
graph.addVertex(T.id, uuid, 'label', 'vertexLabel');
```
**Querying the Vertex with the UUID**
```groovy
# In this query:
# myUUID is the UUID of the vertex you are looking for. You should replace "your-uuid-here" with the actual UUID string.
# g.V(myUUID) is the traversal that looks for a vertex with the given UUID.

UUID myUUID = UUID.fromString("your-uuid-here"); // Replace with your UUID
Vertex myVertex = g.V(myUUID).next();

```

## Datatype supported for Vertex and edge id's
In TinkerPop, you can use Integer and String data type as an identifier for a vertex and edge
```groovy
g.addV('vertexLabel').property(T.id, 123).next()
# Query vertx by id
g.V(123).next()
```

> **Note**: that not all TinkerPop-enabled graph databases  support Integer and 
> String data type as vertex id. For exampe Neptune only support String data type as id

- Some graphs don't allow setting the ID, you have to  set custome propperty and use it as id, see example below:
  - Creating a Vertex with a Custom Integer ID Property:
  ```groovy
  g.addV('vertexLabel').property('myCustomId', 123).next()
  
  # Following query finds the vertex with the label 'vertexLabel'
  # and a custom property 'myCustomId' with the value 123.
  g.V().has('vertexLabel', 'myCustomId', 123).next()

  - ```