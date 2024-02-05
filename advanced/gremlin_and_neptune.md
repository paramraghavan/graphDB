# Gremlin and Neptune

## Transactions

Neptune opens a new transaction at the beginning of each Gremlin traversal and closes the transaction upon the
successful completion of the traversal. The transaction is rolled back when there is an error.

Multiple statements separated by a semicolon (;) or a newline character (\n) are included in a single transaction. Every
statement other than the last must end with a next() step to be executed. Only the final traversal data is returned.

Manual transaction logic using tx.commit() and tx.rollback() is not supported.


## Vertex and edge IDs

Neptune Gremlin Vertex and Edge IDs must be of type String. These ID strings support Unicode characters, and cannot
exceed 55 MB in size.

User-supplied IDs are supported, but they are optional in normal usage. If you don't provide an ID when you add a vertex
or an edge, Neptune generates a UUID and converts it to a string, in a form like this: "48af8178-50ce-971a-fc41-8c9a954cea62". 
These UUIDs do not conform to the RFC standard, so if you need standard UUIDs you should generate them externally and 
provide them when you add vertices or edges.

>**Note:**  The Neptune Load command requires that you provide IDs, using the ~id field in the Neptune CSV format.

>> Reference https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-differences.html#feature-gremlin-differences-transactions

### User-supplied IDs
User-supplied IDs are allowed in Neptune Gremlin with the following stipulations.
* Supplied IDs are optional.
* Only vertexes and edges are supported.
* Only type String is supported.

To create a new vertex with a custom ID, use the property step with the id keyword: g.addV().property(id, 'customid').
> **Note:** Do not put quotation marks around the id keyword. It refers to T.id.

All vertex IDs must be unique, and all edge IDs must be unique. However, _Neptune does allow a vertex and an edge to have
the same ID._

If you try to create a new vertex using the g.addV() and a vertex with that ID already exists, the operation fails. The
exception to this is if you specify a new label for the vertex, the operation succeeds but adds the new label and any
additional properties specified to the existing vertex. Nothing is overwritten. A new vertex is not created. The vertex
ID does not change and remains unique.
```gremlin
g.addV('label1').property(id, 'customid')
g.addV('label2').property(id, 'customid')
g.V('customid').label()
==>label1::label2
```

## Updating a vertex property
To update a property value without adding an additional value to the set of values, specify single cardinality in the property step.
This removes all existing values for the property.
```gremlin
g.V('exampleid01').property(single, 'age', 25)
```

## Labels

Neptune supports multiple labels for a vertex. When you create a label, you can specify multiple labels by separating
them with ::. For example, g.addV("Label1::Label2::Label3") adds a vertex with three different labels. The hasLabel step
matches this vertex with any of those three labels: hasLabel("Label1"), hasLabel("Label2"), and hasLabel("Label3").

>**Note:** The :: delimiter is reserved for this use only. You cannot specify multiple labels in the hasLabel step. 
> For example, hasLabel("Label1::Label2") does not match anything.



>> Reference: https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-differences.html