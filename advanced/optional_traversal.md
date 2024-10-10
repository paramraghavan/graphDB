#Optional Repeat
You want to apply the repeat step only if more nodes exist beyond the current point. We do this
using a combination of `optional()` and `repeat()`:

```gremlin
g.V()
 // ... (your previous steps here)
 .hasLabel('asset')
 .map(
   __.optional(
     __.repeat(__.outE().inV())
       .emit()
   )
 )
 .path()
```

Let's break down this approach:

1. We start with your existing traversal up to the `hasLabel('asset')` step.

2. We use `map()` to apply a sub-traversal to each asset vertex.

3. Inside `map()`, we use `optional()`. This step will:
    - Execute the traversal inside it if possible (if there are outgoing edges).
    - Return the input (the asset vertex) if the traversal inside fails (no outgoing edges).

4. Inside `optional()`, we have the `repeat(__.outE().inV()).emit()` step. This will:
    - Traverse outgoing edges and their incoming vertices if they exist.
    - Emit each step of the traversal.

5. Finally, we use `path()` to get the full path for each result.

This approach accomplishes the following:

- For leaf nodes (assets with no outgoing edges), it will return just the path to that asset.
- For assets with downstream connections, it will return multiple paths: one for the asset itself and others including
  the downstream connections.

The key advantage of this method is that the `repeat()` step is only applied when there are actually more nodes to
traverse. If an asset has no outgoing edges, the `optional()` step ensures we still get a result for that asset.

If you need to filter the edges being traversed, you can still do so within the `outE()` step:

```gremlin
g.V()
 // ... (your previous steps here)
 .hasLabel('asset')
 .map(
   __.optional(
     __.repeat(__.outE('specific_label').inV())
       .emit()
   )
 )
 .path()
```

This version will only traverse edges with the label 'specific_label'.

## Above optional usage  breaks the links outgoing from asset node to nodes returned in the optional section

```gremlin
g.V()
 // ... (your previous steps here)
 .hasLabel('asset')
 .map(
   __.union(
     __.identity(),
     __.optional(
       __.repeat(__.outE().inV())
         .emit(__.outE())
     )
   )
 )
 .path()
```
### Inside map(), we use union() to combine two traversals:

__.identity(): This ensures we always get a path that includes just the asset vertex, even if it has no outgoing edges.
__.optional(...): This wraps the repeat traversal, ensuring it's only applied if there are outgoing edges.

### Inside optional(), we have:

repeat(__.outE().inV()): This traverses from the vertex to its outgoing edges, then to the connected vertices.
emit(__.outE()): This emits the path at each outgoing edge, ensuring that edges are included in the path.