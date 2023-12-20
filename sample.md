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
