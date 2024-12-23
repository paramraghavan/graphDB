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

### When running above queries in gremli-pythosn appemd .toList(), as gremlin does *lazy evaluation**
**lazy evaluation** - plays a crucial role in how queries are constructed and executed. Gremlin is designed to build up a 
traversal (a sequence of steps) and only execute it when a terminal step (an action that triggers execution) is reached.

```python
 # This line sends the query to the Gremlin server and waits for the results. 
 # The toList() method is crucial as it triggers the actual execution of the query.
results = g.V()...toList()
for path in results: 
 print(path)  # This iterates over the returned results and prints them.


## outE() vs out()
### outE()
- outE() is typically used in graph databases or graph traversal frameworks to retrieve the outgoing edges of a vertex or node.
- It returns all the edges that originate from the vertex, providing information about the relationships the vertex has with other vertices.
- This function returns a collection or list of outgoing edges as its result.

### out()
- out() is used to retrieve the neighboring vertices that are connected to the current vertex via outgoing edges.
- It returns all the vertices that can be reached by following the outgoing edges from the current vertex.
- This function returns a collection or list of neighboring vertices as its result.


```
Vertex A
  |
  |--Edge1---> Vertex B
  |
  |--Edge2---> Vertex C
  |
  |--Edge3---> Vertex D

```
* If you use outE() on Vertex A, it will return [Edge1, Edge2, Edge3].
* If you use out() on Vertex A, it will return [Vertex B, Vertex C, Vertex D].


## repeat and Until
In Gremlin, the repeat step is used for iterative traversal in a graph database. It allows you to perform a sequence of traversal
steps multiple times until a specified condition is met. The until step is often used in conjunction with repeat to define the 
termination condition.

```gremlin
Vertex: New York
Vertex: Boston
Vertex: Philadelphia
Vertex: Washington D.C.

Edge: New York - Road -> Boston
Edge: New York - Road -> Philadelphia
Edge: Philadelphia - Road -> Washington D.C.
Edge: Boston - Road -> Philadelphia
```

Find all the cities that can be reached from New York by following roads until you reach a city that starts with the letter "W." 
You can use repeat to achieve this:
```gremlin
g.V().has('name', 'New York').repeat(out('Road').simplePath()).until(has('name', startingWith('W'))).values('name')

```
- g.V().has('name', 'New York') starts the traversal at the New York vertex.
- repeat(out('Road').simplePath()) repeats the traversal step of going out on 'Road' edges while ensuring that we follow a simple path (avoiding revisiting vertices to prevent infinite loops).
- until(has('name', startingWith('W'))): The until step defines the termination condition, which is when we reach a city whose name starts with 'W'.
- values('name') retrieves the names of the cities in the result.

In this case, it would return **"New York," "Philadelphia," and "Washington D.C."**

## repeat and times
Suppose you have a graph with vertices representing locations and edges representing routes between them. 
You want to find all locations that can be reached from a starting location by following routes up to a maximum of 3 hops. 
You can use repeat with times to achieve this:
```groovy
g.V().has('name', 'Start Location')
  .repeat(out()).times(3)
  .values('name')
```

## repeat and emit
A graph with vertices representing locations and edges representing routes between them. You want to find all locations reachable 
from a starting location by following routes, and you want to emit the locations at each step of the traversal until you reach a 
location with a certain property (e.g., a location with the property 'end' set to true). 

You can use repeat with emit to achieve this:
```gremlin
g.V().has('name', 'Start Location')
  .emit() // Emit the starting location
  .repeat(out())
  .has('end', true) // Termination condition: Reach a location with 'end' property set to true
  .emit() // Emit the location that meets the termination condition
  .values('name')
```

- g.V().has('name', 'Start Location') starts the traversal at the vertex with the name 'Start Location'.
- .emit() emits the starting location, ensuring that it's included in the result.
- .repeat(out()) specifies that you want to repeat the traversal step of going out on any edge (out()).
- .has('end', true) defines the termination condition, which is when you reach a location with the 'end' property set to true.
- .emit() emits the location that meets the termination condition.
- .values('name') retrieves the names of the locations in the result.


## path()

```gremlin
# Understanding Traversals:
g.V().hasLabel('Person').out('knows').hasLabel('Person').path().limit(5)

# Finding Paths:
g.V().has('name', 'A').repeat(out()).until(has('name', 'D')).path()

# Analyzing Relationships:
g.V().has('name', 'Alice').outE().inV().path()

# Finding Shortest Paths:
g.V().has('name', 'A').repeat(out().simplePath()).until(has('name', 'D')).path().limit(1)

```

## fold
The fold() step in Gremlin is used to aggregate the results of a traversal into a list. It's especially useful when you want to convert a 
stream of elements into a single collection. 


* g.V().hasLabel('person'): Select all vertices with the label 'person'.
* values('name'): Extract the 'name' property from these vertices.
* fold(): Aggregate all the names into a list.
* 
```gremlin
g.V().hasLabel('airport').values('name').fold()
#output
['Los Angeles International Airport', 'John F. Kennedy International Airport', 'Hartsfield-Jackson Atlanta International Airport',...]

```

### Counting Elements with fold()

* g.V().hasLabel('airport'): Select all vertices labeled as 'airport'.
* out('route'): Traverse to the vertices that each airport route to destination.
* fold(): Aggregate these routes into a list for each airport.
* count(local): Count the number of elements in each list.

```gremlin 
g.V().hasLabel('airport').out('route').fold().count(local)
```

### Creating a Map of Vertex Properties
* g.V(): Select all vertices.
* group(): Group the results.
* by(id): Use the vertex ID as the key.
* by(valueMap().fold()): Use a map of all properties as the value, aggregated into a list.

```gremlin
g.V().group().by(id).by(valueMap().fold())
#output
{40001: [{'code': ['LAX'], 'name': ['Los Angeles International Airport']}], 40002: [{'code': ['JFK'], ...,  40025: [{'code': ['SYD'], 'name': ['Sydney Airport']}]}
```

## show all the properties of vertices and edges

```gremlin
# show all the properties of vertices 
# g.V() selects all vertices.
# valueMap() fetches the properties of these vertices.
# with(WithOptions.tokens) includes the vertex IDs and labels in the output.
g.V().valueMap().with(WithOptions.tokens)

# show all the properties of edges
# g.E() selects all edges.
# valueMap() fetches the properties of these edges.
# with(WithOptions.tokens) includes the edge IDs and labels in the output.
g.E().valueMap().with(WithOptions.tokens)

```

## next vs iterate
- Use .next(), when you need the result (and you are expecting exactly one result)
- Use .iterate(), when you don't need the result (typically mutation queries, that add/change properties, edges and/or vertices).