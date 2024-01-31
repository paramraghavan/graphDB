# Graph and Schema

In a graph database, a schema design visually represents how different entities (vertices) are connected by relationships (edges). 
Unlike traditional relational database schemas, graph database schemas focus on the relationships between entities as much 
as the entities themselves.

## Vertex
Each type of entity in your graph is represented as a vertex. For example:
- User
- Product
- Order
- Category

## Edges
The relationships between vertices are represented as edges. Example see below:

- User -[PLACED]-> Order
- Order -[CONTAINS]-> Product
- Product -[BELONGS_TO]-> Category
- User -[FOLLOWS]-> User


## Properties
Both vertices and edges can have properties, which are key-value pairs that store additional information. For example:

- User: {name, email, joinDate}
- Product: {name, price, description}
- Order: {orderDate, status}
- PLACED: {date, totalAmount}

## Indices and Constraints

With Amazon Neptune, creating and using indexes for vertices and edges is quite different from traditional relational databases.
Neptune automatically manages indexes to optimize the performance of graph queries. Users do not create indexes in the 
traditional sense (like creating an index on a column in a relational database). Instead, Neptune uses a system of internal 
indexing based on the graph data model to efficiently execute queries. The indexing is optimized for typical graph query

### Schema Constraints
Within Neptune, the only schema constraint available is the uniqueness of the ID of a node or edge. There is no feature to specify any additional schema constraints,
or any additional uniqueness or value constraints on an element in the graph. ID values in Neptune are strings and may be set using Gremlin, like this:

```gremlin
g.addV('person').property(id, '1') )
```

Applications that need to leverage the ID as a uniqueness constraint are encouraged to try this approach for achieving a uniqueness constraint. 
If the application used multiple columns as a uniqueness constraint, the ID may be set to a combination of these values. For example id=123, code='SEA' 
could be represented as ID='123_SEA' to achieve a complex uniqueness constraint.
       

## Schema Diagram Example
A simple e-commerce graph schema:

- Vertices: User, Product, Order
- Edges: User -[PLACED]-> Order, Order -[CONTAINS]-> Product, User -[VIEWED]-> Product
- Properties: User (name, email), Product (name, price), Order (date, total), PLACED (date), VIEWED (timestamp)

A diagram might look like this:
```sccs
[User] --(PLACED)--> [Order] --(CONTAINS)--> [Product]
  |                                             ^
  |                                             |
  +----------------------(VIEWED)---------------+
```


## Summary
A graph database schema is more flexible and less rigid than a traditional relational database schema. It's often 
designed with the **specific queries and traversal patterns in mind** that will be used to interact with the data.
