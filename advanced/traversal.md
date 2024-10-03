# Problem:
my graph has the following structure:
td node - root
td node can have: * tde * interim
tde node - this node can end here  or it  can have asset node  or can have one more interim nodes
interim node - this node end here or it can have an asset node or it can have one of more interim nodes
asset node - this node has no more nodes down stream to it

## Question
Using gremlin how do i list the entire path down stream from td node where the node property  can  be filtered by a tde or interim, once the filter is applied we the query further queries down stream from the matched node


## Possible answer
```gremlin
g.V().hasLabel('td').as('start').
repeat(
  __.outE().as('preE').inV().as('preV')
).
until(
  __.or(
    __.hasLabel('tde').has('propertyName', 'propertyValue'),
    __.hasLabel('interim').has('propertyName', 'propertyValue')
  )
).as('match').
project('beforeMatch', 'afterMatch').
  by(
    __.path().from('start').to('match').
      by(elementMap())
  ).
  by(
    __.repeat(
      __.choose(
        __.hasLabel('asset'),
        __.identity(),
        __.outE().as('postE').inV().as('postV')
      )
    ).
    until(
      __.or(
        __.hasLabel('asset'),
        __.not(outE())
      )
    ).
    path().from('match').
      by(elementMap())
  ).
dedup()

```

Let's break down this query and explain its components:

1. `g.V().hasLabel('td').as('start')`: Start from all TD nodes and label it as 'start'.

2. `repeat(__.outE().as('preE').inV().as('preV'))`:
   Traverse outgoing edges and vertices before the match.

3.
`until(__.or(__.hasLabel('tde').has('propertyName', 'propertyValue'), __.hasLabel('interim').has('propertyName', 'propertyValue')))`:
Continue until finding a TDE or interim node with the specified property value.
Replace 'propertyName' and 'propertyValue' with your specific criteria.

4. `as('match')`: Label the matched node.

5. `project('beforeMatch', 'afterMatch')`: Create two separate fields in the output.

6. For 'beforeMatch':
   ```gremlin
   __.path().from('start').to('match').by(elementMap())
   ```
   Capture the path from the start to the matched node.

7. For 'afterMatch':
   ```gremlin
   __.repeat(
     __.choose(
       __.hasLabel('asset'),
       __.identity(),
       __.outE().as('postE').inV().as('postV')
     )
   ).
   until(
     __.or(
       __.hasLabel('asset'),
       __.not(outE())
     )
   ).
   path().from('match').
     by(elementMap())
   ```
   This part:
    - Traverses from the matched node.
    - If it's an asset node, it stops (using `identity()`).
    - Otherwise, it continues to the next node.
    - It stops when it reaches an asset node or a node with no outgoing edges.
    - It captures all paths downstream from the matched node.

8. `dedup()`: Remove any duplicate results.

To use this query:

1. Replace 'propertyName' and 'propertyValue' with the specific property and value you're matching for TDE or interim
   nodes.

For example, if you're looking for a TDE or interim node with a 'name' property equal to 'example', it would look like
this:

```gremlin
g.V().hasLabel('td').as('start').
repeat(
  __.outE().as('preE').inV().as('preV')
).
until(
  __.or(
    __.hasLabel('tde').has('name', 'example'),
    __.hasLabel('interim').has('name', 'example')
  )
).as('match').
// ... rest of the query remains the same
```

This query is efficient because:

1. It processes the graph in a single pass.
2. It stops the 'beforeMatch' traversal as soon as it finds the matching node.
3. It handles the various possible structures in your graph (TDE to asset, TDE to interim, interim to asset, interim to
   interim, etc.).
4. It stops traversing when it reaches an asset node or a leaf node.

The output will be a list of maps, each containing:

- 'beforeMatch': The path from the TD node to the matching TDE or interim node.
- 'afterMatch': All paths from the matching node to downstream asset or leaf nodes.

If you want to start from a specific TD node instead of all TD nodes, you can modify the start of the query:

```gremlin
g.V(tdNodeId).hasLabel('td').as('start').
// ... rest of the query remains the same
```

Replace `tdNodeId` with the ID of the specific TD node you want to start from.

This query provides a comprehensive view of the paths both before and after the matching TDE or interim node, giving you
full visibility into the relevant parts of your graph structure while adhering to the specific relationships and
possibilities you described.

## Traverse up adn down the filtered node
To query a graph using Gremlin and filter by a node property to get all nodes upstream and downstream from a specific
node, starting from the root node, you can use a combination of traversal steps.

Gremlin query for upstream and downstream nodes
```gremlin
g.V().hasLabel('root')  // Start from the root node
  .repeat(out())  // Traverse downstream
  .until(has('property', 'value'))  // Until we find the node with the specific property
  .as('target')  // Mark this node as 'target'
  .union(
    __.repeat(__.in()).emit(),  // Traverse upstream from the target node
    __.repeat(out()).emit()  // Traverse downstream from the target node
  )
  .dedup()  // Remove duplicate nodes
  .path()  // Show the full path
```