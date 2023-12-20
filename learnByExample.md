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
