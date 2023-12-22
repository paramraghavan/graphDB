# Example

## Step 1
Creating a sample data set, loading it into a TinkerPop-enabled graph system (like TinkerGraph), and writing a Gremlin query for fraud detection involves several steps.
Let's assume a simple banking fraud detection scenario where we have accounts and transactions. We'll create a small graph where vertices represent accounts and transactions, and edges represent the flow of money.

**Sample data structure:**

- Accounts: Vertices with properties like account ID, account holder name, etc.
- Transactions: Vertices with properties like transaction ID, amount, etc.
- Edges: Representing money transfer from one account to another.

## Step 2
**Load Data into TinkerGraph using Gremlin Console**
Open the Gremlin Console and execute the following commands to create the graph:
```groovy
// Initialize the graph
graph = TinkerGraph.open()
g = graph.traversal()

// Create account vertices
a1 = g.addV('account').property('accountId', 'A1').property('holderName', 'John Doe').property('balance', 10000).next()
a2 = g.addV('account').property('accountId', 'A2').property('holderName', 'Jane Smith').property('balance', 5000).next()
a3 = g.addV('account').property('accountId', 'A3').property('holderName', 'Alice Johnson').property('balance', 7000).next()

// Create transaction vertices (for simplicity, just using IDs and amounts)
t1 = g.addV('transaction').property('transactionId', 'T1').property('amount', 2000).next()
t2 = g.addV('transaction').property('transactionId', 'T2').property('amount', 3000).next()

// Create edges to represent transactions
g.addE('transfers').from(a1).to(t1).property('date', '2021-01-15').next()
g.addE('transfers').from(t1).to(a2).property('date', '2021-01-15').next()
g.addE('transfers').from(a2).to(t2).property('date', '2021-02-20').next()
g.addE('transfers').from(t2).to(a3).property('date', '2021-02-20').next()
```

## Step 3 -Fraud Detection
**Write a Gremlin Query for Fraud Detection**
Let's say we want to find accounts involved in transactions over a certain threshold within a short period.
- Finds transactions over $2000.
- Traces back to the source account and forward to the destination account.
- Selects the names of both accounts involved in these transactions.
  
```groovy
// Detect potential fraud: Accounts involved in transactions over $2000 within a short period
g.V().hasLabel('transaction').has('amount', gt(2000)).as('tx')\
  .inE('transfers').outV().as('src')\
  .select('tx').outE('transfers').inV().as('dest')\
  .select('src', 'dest').by('holderName').by('holderName')
// Result
==>[src:Jane Smith,dest:Alice Johnson]
```

## has step in Gremlin
The has step in Gremlin can be used to filter vertices (or edges) based on either labels or properties, depending on the arguments you provide to it. It's a versatile step that allows you to narrow down your traversal to specific elements that match certain criteria.

### When has Uses Label
- When you provide a single argument to the has step, it is typically used to filter by label.
- For example, g.V().has('airport') would return all vertices that have the label 'airport'.

### When has Uses Property
- When you provide two or three arguments to the has step, it is used to filter by properties.
- For example, g.V().has('airport', 'code', 'JFK') would return all vertices that have the label 'airport' and where the property 'code' is equal to 'JFK'.
- If you use two arguments, like g.V().has('code', 'JFK'), it will return all vertices (regardless of their label) where the property 'code' is 'JFK'.

## Gremlin OutE
In Gremlin, the outE() step is used in a traversal to navigate from a vertex to its outgoing edges. Essentially, it helps you to move from a vertex to the edges that the vertex has directed away from it.

- Starting Point - Vertex: The traversal begins at a vertex (or vertices) you've specified or filtered. This can be a single vertex, a set of vertices, or vertices filtered based on certain criteria.
- Traversal to Outgoing Edges: By applying the outE() step, you move from the vertex to its outgoing edges. These are the edges where the vertex is the "outgoing" or "source" vertex.
- Filtering (Optional): You can filter these edges by their label or properties. For example, outE('knows') would move to all outgoing edges with the label 'knows'.

Example:
```groovy
// Assuming g is your graph traversal source
g.V().hasLabel('person').outE()
g.V().hasLabel('person').outE('knows')

```
- g.V(): Start the traversal with all vertices in the graph.
- .hasLabel('person'): Filter the vertices to only those with the label 'person'.
- .outE(): For each of those person vertices, traverse to all their outgoing edges.
- .outE('knows'): For each of those person vertices, filert all their outgoing edges for edge label 'knows'

## inV()
the inV() step is used in a traversal to navigate from an edge to the vertex at the "in" side of the edge. This step allows you to traverse from an edge to the vertex where the edge is pointing to, also known as the destination or target vertex of the edge.
Example:
```groovy
// Assuming g is your graph traversal source
g.E().hasLabel('knows').inV()
```
- g.E(): Start the traversal with all edges in the graph.
- .hasLabel('knows'): Filter the edges to only those with the label 'knows'.
- .inV(): For each of those 'knows' edges, traverse to the vertex at the "in" side, i.e., the people who are known by someone.

## outV()
The outV() step is used to navigate from an edge to the vertex at the "out" side of the edge. This step allows you to traverse from an edge to its source or originating vertex - essentially, the vertex where the edge starts from.
Example:
```groovy
// Assuming g is your graph traversal source
g.E().hasLabel('knows').outV()
```
- g.E(): Starts the traversal with all edges in the graph.
- .hasLabel('knows'): Filters the edges to only include those with the label 'knows'.
- .outV(): For each of those 'knows' edges, traverses to the vertex at the "out" side, which represents the people who know someone else.


## Querying Vertices
- List All Vertices:
```groovy
g.V().toList()
```
- List All Accounts:
```groovy
g.V().hasLabel('account').valueMap().toList()
```
- Find a Specific Account by Property (e.g., Account ID):
```groovy
g.V().has('account', 'accountId', 'A1').valueMap().toList()
```

## Querying Edges
- List All Edges:
```groovy
g.E().toList()
```
- List All Transfer Edges:
```groovy
g.E().hasLabel('transfers').valueMap().toList()
```
- Find Transfers from a Specific Account:
This will find all transfer edges originating from the account with ID 'A1'.
```groovy
g.V().has('account', 'accountId', 'A1').outE('transfers').valueMap().toList()

```

## Querying Relationships
- Find All Transactions from a Specific Account:
This will find all transaction vertices that are connected to the account 'A1' via outgoing 'transfers' edges.
```groovy
g.V().hasLabel('account').outE('transfers').inV().valueMap().toList()
```




## Explain - g.V().has('account', 'accountId', 'A1').outE('transfers').inV()
- g.V().has('account', 'accountId', 'A1'): This part of the query selects the **vertex** (or vertices) that have a label 'account' and where the property 'accountId' is 'A1'. Essentially, it's finding the account with ID 'A1' node/vertex.
- .outE('transfers'): After selecting the account vertex, this step moves to the **outgoing edge**s from that vertex with the label 'transfers'. It's essentially looking for all the transfer operations that originated from account 'A1'.
- .inV(): Finally, this step moves from those edges to the vertex at the other end of each edge – the "in" vertex. In the context of our data model, where edges represent money transfers, this would effectively find all the transactions or accounts that received transfers from account 'A1'.
- if account 'A1' transferred money to transaction 'T1', the query g.V().has('account', 'accountId', 'A1').outE('transfers').inV() would start at 'A1', follow the 'transfers' edge, and end up at 'T1'.
In graph terminology, an edge has a direction from an "out" vertex to an "in" vertex. The outE() step moves in the direction of the edge, from the "out" vertex to the edge itself, while inV() continues along the edge to reach the "in" vertex. This is fundamental to navigating and querying in graph databases using Gremlin.

## Explain - g.V().has('account', 'accountId', 'A1').outE('transfers').valueMap().toList()
- g.V(): This step starts the traversal at all vertices in the graph. V stands for vertices, and g is typically your graph traversal source.
- .has('account', 'accountId', 'A1'): This filters the vertices selected in the first step. It only includes vertices that have a label 'account' and where the property 'accountId' is equal to 'A1'. Essentially, this step narrows down the traversal to the specific account vertex with the ID 'A1'.
- .outE('transfers'): After finding the account vertex, this step moves to the edges that are outgoing from that vertex and have the label 'transfers'. In a graph that represents financial transactions, these edges represent money transfers originating from account 'A1'.
- .valueMap(): This step is used to extract the properties of the elements (in this case, the edges found in the previous step) as a map. For each edge, it will create a map where the keys are the property names and the values are the property values.
- .toList(): This is a terminal step that collects the results of the traversal into a list and returns it. This is useful when you want to output the results for further processing or examination in a format that's easy to handle, like a list.
```groovy
//Result
//==>[date:2021-01-15]
```

## Explain -  g.V().hasLabel('account').outE('transfers').valueMap().toList()
```groovy
//Result
//==>[date:2021-01-15]
//==>[date:2021-02-20]
```

## Show vertex labels and properties
```groovy
g.V().valueMap().with(WithOptions.tokens)
//Result:
//==>{id=0, label=account, accountId=[A1], holderName=[John Doe], balance=[10000]}
//==>{id=18, label=transaction, amount=[1500], transactionId=[T3]}
//==>{id=4, label=account, accountId=[A2], holderName=[Jane Smith], balance=[5000]}
//==>{id=8, label=account, accountId=[A3], holderName=[Alice Johnson], balance=[7000]}
//==>{id=12, label=transaction, amount=[2000], transactionId=[T1]}
//==>{id=15, label=transaction, amount=[3000], transactionId=[T2]}
```

## Explain - g.V().has('account', 'accountId', transfer['fromAccountId']).next()
- g.V().has('account', 'accountId', transfer['fromAccountId']): This part of the traversal finds vertices that have a label 'account' and where the property 'accountId' matches the value in transfer['fromAccountId'].
- .next(): This step retrieves the first vertex (or the next vertex) that matches the criteria from the traversal. If there are multiple vertices that match, next() will return the first one it encounters. If no vertices match, it will throw a NoSuchElementException.

### Use Cases of next()
- Retrieving a Single Element: When you're sure the traversal will return a single element, or you are only interested in the first element of the potential results.
- Step-by-Step Iteration: In scenarios where you want to manually iterate over elements, retrieving one at a time.
- next(), you'll only get the first result. 
- toList() - If you need all results or iterating over the traversal with a loop are more appropriate.

### For loop
```python
# Iterate through the vertices using a for loop:
vertices = g.V().hasLabel('account').toList()
for vertex in vertices:
    print(vertex)
```

## iterate()? - g.addV('airport').property('code', 'LAX').property('name', 'Los Angeles International Airport').iterate()
Using iterate() is particularly important in scenarios where the result of the traversal is not of interest, but the side effects (like adding or modifying elements in the graph) are.

- In Gremlin, the iterate() step is used at the end of a traversal to force the execution of the traversal. Gremlin traversals are lazy, meaning they are not executed until you explicitly request the results or iterate over them. This design is beneficial for building up complex traversals without incurring the cost of execution until absolutely necessary.
- When you use addV() or other mutating steps like addE(), property(), etc., they only prepare the traversal but do not actually commit the changes to the graph. The iterate() step is used to finalize and execute these traversals, causing the mutations to be applied to the graph.
- addV('airport'): Prepares to add a vertex with the label 'airport'.
- property('code', 'LAX'), property('name', 'Los Angeles International Airport'): Adds properties to the new vertex.
- iterate(): Executes the traversal, actually adding the vertex with its properties to the graph.
- Without iterate(), the vertex creation and property assignments would be defined but not executed, so the vertex would not actually be added to the graph.

### In Gremlin, there are different ways to initiate the execution of a traversal. Some common ones include:
- toList(), next(), toSet(), etc., which are typically used when you want to retrieve the results of a traversal.
- iterate(), which is used when you don't need the results (like in mutations) but want to ensure the traversal is executed.

