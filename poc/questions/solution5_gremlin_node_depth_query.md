
# Gremlin Query to Return Node Depth

In Gremlin, you can return the **depth** of a node (vertex), which represents how many edges (hops) it is away from a starting vertex in the traversal. This is typically done by counting the number of edges traversed from the root node to each node. Here’s how you can track and return the depth of nodes using Gremlin.

## Example Gremlin Query to Get Node Depth

```groovy
g.V(startingVertexId)
  .repeat(out())    // Traverse outward (depth-first search)
  .emit()           // Emit each node along the way
  .path()           // Capture the path from start to current node
  .project('node', 'depth')
    .by(identity())   // Return the current node
    .by(path().count(local).is(gt(1)).map { it.get() - 1 }) // Depth = path length - 1
```

### Explanation:

- **`g.V(startingVertexId)`**: Starts the traversal from a given vertex, which could be your root node (replace `startingVertexId` with the actual starting vertex ID).
- **`repeat(out())`**: Repeats the outward traversal through connected vertices (i.e., moving to child nodes). You can change `out()` to `in()` or `both()` depending on the direction of the edges you want to follow.
- **`emit()`**: Ensures that each node is emitted (included in the result set) as it is encountered during the traversal.
- **`path()`**: Captures the full path from the starting node to each encountered node, which allows us to calculate the depth.
- **`project()`**: Projects two values in the result: the node (`identity()`) and its depth.
- **`path().count(local)`**: Returns the number of steps in the path (which corresponds to the depth + 1, as the path includes the root node itself).
- **`is(gt(1)).map { it.get() - 1 }`**: Subtracts 1 from the path length to calculate the depth, since the starting node is depth 0.

## Example Output:
```json
[
  { "node": { "id": "1", "label": "root" }, "depth": 0 },
  { "node": { "id": "2", "label": "child1" }, "depth": 1 },
  { "node": { "id": "3", "label": "child2" }, "depth": 2 },
  { "node": { "id": "4", "label": "grandchild1" }, "depth": 3 }
]
```

## Customizations:
- **Direction of Traversal**: Use `out()`, `in()`, or `both()` to adjust the direction of traversal.
- **Edge Type Filtering**: Use `outE('edgeLabel').inV()` to filter the traversal based on specific edge labels.
- **Depth Limit**: You can control the maximum depth with `repeat().times(n)` to limit traversal to a certain number of hops.

This pattern can be useful when navigating hierarchical or tree-like structures in a graph.
