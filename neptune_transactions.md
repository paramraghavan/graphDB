# Neptune and Transactions
Neptune supports both the Apache Tinkerpop Gremlin stack and the RDF/SPARQL W3C standards.
It takes range locks using gap locks, which are locks on a gap between index records.

In Gremlin, Neptune classifies a query as a read-only query or a mutation query based on whether it contains any query-path steps such as addE(), addV(), property(), or drop() that manipulates data. 
If the query contains any such path step, it is classified and executed as a mutation query.

## Transactions

- https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-transactions.html
- https://docs.aws.amazon.com/neptune/latest/userguide/transactions.html
