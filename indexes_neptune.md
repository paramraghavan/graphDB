# Neptune and Indexes
In Amazon Neptune, creating and using indexes for vertices and edges is quite different from traditional relational databases.
Neptune automatically manages indexes to optimize the performance of graph queries. Users do not create indexes in the 
traditional sense (like creating an index on a column in a relational database). Instead, Neptune uses a system of internal 
indexing based on the graph data model to efficiently execute queries. The indexing is optimized for typical graph query 
access patterns, such as:
* Looking up a vertex or edge by its ID.
* Traversing relationships (edges) from a given vertex.
* Querying vertices or edges based on property values.

>While **you can't use the explain()** step in Neptune to analyze query execution plans, understanding how Neptune 
> automatically manages indexes can help you write efficient queries. 

**Neptune's Indexing Mechanism**
- **Graph Data Model**: Neptune uses a quad-based graph data model, with each quad consisting of **subject (S), predicate (P), object (O), 
and graph (G) positions**. This model is foundational for how data is indexed and queried.
- **Automatic Index Creation:** Neptune automatically creates and maintains certain indexes based on this quad model. 
By default, it maintains three indexes - **SPOG, POGS, and GPSO**. These indexes optimize common access patterns in graph queries.
- **Index Types:** Neptune uses three primary index types by default: SPOG, POGS, and GPSO. These indexes are sufficient for many common graph query patterns.
  - SPOG: Subject + Predicate + Object + Graph
  - POGS: Predicate + Object + Graph + Subject
  - GPSO: Graph + Predicate + Subject + Object
- **Index Usage:** When you run a query in Neptune, the system utilizes these indexes to efficiently locate the data. 
The choice of index depends on the query's structure and the known positions within that query.

**Quad  attributes used  in Amazon Neptune**

A "quad" consists of four components: subject, predicate, object, and graph. Let's breakdown
each of these components in the context of a graph involving airports and flight routes:

- Subject (S): 
  - It's typically a vertex. In a graph representing airports and routes, an airport would be a subject. For instance, 
a **vertex representing "JFK Airport"** would be the subject of various edges.
- Predicate (P)
  - It defines the type of relationship between the subject and the object. In our airport graph, a predicate 
might be "routeTo" for an edge that connects two airport vertices, indicating a flight route from one airport to another.
- Object (O)
  - The object is the vertex/node that is related to the subject via the predicate. with the airport graph, the object could be another airport to which there is a route. 
For instance, if JFK Airport (subject) has a route (predicate) to LAX Airport, then LAX Airport is the object.
- Graph (G)
  - This component is used to denote the context or subgraph to which the statement belongs. If the data is divided by regions or types of flights (e.g., domestic, international), the "Graph" 
component could be used to differentiate between these. A statement might belong to the "International Flights" graph or the "Domestic Flights" graph.

**Applying Quads in Neptune:**

Here is a quad: (JFK Airport, hasRouteTo, LAX Airport, International Flights). This quad states that there is an international route (predicate) from JFK Airport (subject) to LAX Airport 

**Examples of Index usage**
- Querying Vertex Properties:
  - Query: Find properties of a specific vertex.
  - Gremlin Query: g.V('vertexId').properties()
  - Neptune Index Used: SPOG index, as the subject (vertex ID) is known.

## Predicates wrt Amazon Neptune and graph databases
Predicates are often the labels on the edges that define the type of relationship between two vertices. For example consider a social network graph,
Vertices are People and Edges are Relationships between people.

### Predicate as Edge Label:
- If Person A "knows" Person B, the edge connecting A to B would have a predicate (edge label) of "knows."
- If Person A "follow" Person B, the edge connecting A to B would have a predicate of "follows."

In Gremlin, you might query these relationships as follows:
- To find who Person A knows: g.V('PersonA').out('knows')
- To find who knows Person A: g.V('PersonA').in('knows')
- To find who Person A follows: g.V('PersonA').out('follows')

## Example Use Cases for quad indexes
* Finding Vertex Labels: 
  * For a query like g.V('v1').label(), Neptune uses the SPOG index. The pattern here is (<v1>, <~label>, ?, ?), where the known positions are subject and predicate.
  * For Query: g.V('vertexId').properties(), Neptune Index Used: SPOG index, as the subject (vertex ID) is known.
    * S (Subject): <v1> - This is known and represents the vertex ID. 
    * P (Predicate): <~label> - This represents the label property of the vertex. 
    * O (Object): ? - This is what we are querying for (the actual label of the vertex). 
    * G (Graph): ? - Assuming the graph context is not specifically targeted in the query.
* Finding Out-Edges: 
  * For a query like g.V('v1').out('knows'), the pattern is (<v1>, <knows>, ?, ?). The SPOG index is used again, utilizing the known subject and predicate positions. 
  * Query: Find edges between two specific vertices - g.V('sourceVertexId').outE().where(inV().hasId('targetVertexId')). 
Neptune Index Used: SPOG index, as it starts with a known vertex and looks for outgoing edges.
* Finding Vertices by Label: 
  * For a query like g.V().hasLabel('Person'), the pattern is (?, <label>, <Person>, <>), and Neptune uses the POGS index.
    * Predicate (P): Represented by <~label>. This indicates that we are looking at the type of the vertex, which is a special kind of predicate in graph databases. The '~label' is a system-generated predicate used to denote the label of a vertex. 
    * Object (O): Represented by <Person>. This specifies the label we are filtering by, which in this case is 'Person'. 
    * Subject (S) and Graph (G): Represented by ? and <~>, respectively. Both are unspecified in this query, as we are not filtering based on a particular vertex (subject) or a specific subgraph (graph). The <~> in the graph position is a placeholder used by Neptune to represent the default graph context or an unspecified graph context.
  * Here, the predicate, object, and graph positions are known.
  
* Find all vertices with a specific property value.
  * Query: g.V().has('propertyName', 'value')
  * Neptune Index Used: POGS index, as the property name and value are known.
* Finding Adjacent Vertices of an Edge: 
  * A query like g.E('e1').bothV() would use the GPSO index with a pattern of (?, ?, ?, <e1>).
* Find incoming edges to a vertex.
  * Gremlin Query: g.V('vertexId').inE()
  * Neptune does not have a reverse traversal OSGP index, which would be ideal for this query. 
If your graph has many distinct predicates, enabling the OSGP index using Lab Mode may improve performance.


## Explain Index Pattern (?, ?, ?, <e1>) 
This pattern is a representation of how Neptune uses its GPSO index to process the query. Each question mark or the 
value in the pattern corresponds to a part of the quad-based data model used by Neptune: Graph (G), Predicate (P), Subject (S), and Object (O).

- Graph (G): Represented by the first question mark (?). In this specific query, the graph context is not specified, hence the question mark indicating an unspecified or wildcard value.
- Predicate (P): Represented by the second question mark (?). Similarly, the predicate is not specified in the query, as we are not filtering by the type of relationship (predicate) but rather by a specific edge.
- Subject (S): Represented by the third question mark (?). The subject is also unspecified because the query is looking for both vertices connected by the edge, regardless of which is the subject or object in the relationship.
- Object (O): Represented by <e1>. This is the only specified part of the pattern, indicating that we are looking for information specifically related to the edge 'e1'.
