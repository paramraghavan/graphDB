# Gremlin and Neptune

## Gremlin Transactions in Neptune
 Our requests most  likely made using text-based Gremlin strings
- Using the Java driver, Python driver and Client.submit(string).
- Using the Gremlin console and :remote connect.
- Using the HTTP API.
- Request made via Gremlin python driver in gremlinpython library

Neptune opens a new transaction at the beginning of each Gremlin traversal and closes the transaction upon the
successful completion of the traversal. The transaction is rolled back when there is an error.

Multiple statements separated by a semicolon (;) or a newline character (\n) are included in a single transaction. Every
statement other than the last must end with a next() step to be executed. Only the final traversal data is returned.

### Gremlin Language Variants (GLV) support Gremlin's tx()

After TinkerPop 3.5.x, the transaction can be explicitly controlled and the session managed transparently. Gremlin
Language Variants (GLV) support Gremlin's tx() syntax to commit() or rollback() a transaction as follows:

## Using java driver
```java
GraphTraversalSource g = traversal().withRemote(conn);

Transaction tx = g.tx();

// Spawn a GraphTraversalSource from the Transaction.
// Traversals spawned from gtx are executed within a single transaction.
GraphTraversalSource gtx = tx.begin();
try {
    gtx.addV('person').iterate();
    gtx.addV('software').iterate();

    tx.commit();
} finally {
    if (tx.isOpen()) {
        tx.rollback();
    }
}
```
## Using python and gremlin_python library
>> ref: https://tinkerpop.apache.org/docs/current/reference/#gremlin-python-transactions
```python
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

# Connect to Gremlin Server
g = traversal().withRemote(DriverRemoteConnection('ws://localhost:8182/gremlin', 'g'))
# 2 vertex additions in three individual requests/transactions:
try:
    g.addV('person').property('name', 'John').iterate()
except Exception as e:
    print(f"An error occurred: {e}")   
try:    
    g.addV('person').property('name', 'Bob').iterate()
except Exception as e:
    print(f"An error occurred: {e}") 

try:
    # 3 vertex additions in one single request/transaction::
    g.addV('person').property('name', 'John').\
    addV('person').property('name', 'Bob').\
    addV('person').property('name', 'Bill').iterate()
        
except Exception as e:
    print(f"An error occurred: {e}")
```

#### tx(), tx,rollback, commit are all not implemented in gremlin python
```python
# This does not work fails @ g.tx(), tx,rollback, commit are all not implemented in
# gremlin python.
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

g = traversal().with_remote(DriverRemoteConnection('ws://localhost:8182/gremlin'))

# Create a Transaction.
tx = g.tx()

# Spawn a new GraphTraversalSource, binding all traversals established from it to tx.
gtx = tx.begin()

try:
    # Execute a traversal within the transaction.
    gtx.add_v("person").property("name", "Lyndon").iterate(),

    # Commit the transaction. The transaction can no longer be used and cannot be re-used.
    # A new transaction can be spawned through g.tx().
    # The context of g remains sessionless throughout the process.
    tx.commit()
except Exception as e:
    # Rollback the transaction if an error occurs.
    tx.rollback()
```
## python submit using client handler
```python
from gremlin_python.driver import client 
client_handler = None
client_handler = client.Client('ws://localhost:8182/gremlin', 'g') 

# result_set = client_handler.submit('[1,2,3,4]')  
# future_results = result_set.all()  
# results = future_results.result() 
# assert results == [1, 2, 3, 4] 
# 
# future_result_set = client_handler.submit_async('[1,2,3,4]') 
# result_set = future_result_set.result() 
# result = result_set.one() 
# assert results == [1, 2, 3, 4] 
# assert result_set.done.done() 

try:
    insert_query = "g.addV('person').property('name', 'John').addV('person').property('name', 'Bob').addV('person').property('name', 'Bill').iterate()"    
    client_handler.submit(insert_query).all()      
except Exception as e:
    print(e)  
finally:
    if client_handler != None:
        client_handler.close()

client_handler.close() 
```


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
* Only type String is supported.

To create a new vertex with a custom ID, use the property step with the id keyword: g.addV().property(id, 'customid').
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
> https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-transactions.html
> https://docs.aws.amazon.com/neptune/latest/userguide/transactions.html
