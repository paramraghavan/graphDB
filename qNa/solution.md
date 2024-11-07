We have a complex graph where source assets go through 7-10 layers of transformations, with multiple
source nodes (100 elements) converging into a single consumer asset node. 

```groovy
// Option 1: Simple path traversal with depth control
g.V().
  hasLabel('asset').
  has('id', 'consumer-asset-id').  // Start from consumer asset
  repeat(
    inE().
    outV().
    simplePath()  // Prevent cycles
  ).
  until(
    or(
      hasLabel('source_asset'),
      loops().is(gte(10))  // Max depth safety
    )
  ).
  path().
  by(valueMap('id', 'name', 'type'))  // Add relevant properties

// Option 2: Optimized for Neptune with batching and property filtering
g.V().
  hasLabel('asset').
  has('id', 'consumer-asset-id').
  project('consumer', 'lineage').
  by(valueMap(true)).
  by(
    repeat(
      union(
        inE().
        project('transformation', 'source').
        by(valueMap('type', 'timestamp')).
        by(outV().valueMap(true))
      ).fold()
    ).
    until(
      or(
        hasLabel('source_asset'),
        loops().is(gte(10))
      )
    ).
    path()
  )

// Option 3: Find all source assets with transformation details
g.V().
  hasLabel('asset').
  has('id', 'consumer-asset-id').
  project('consumer', 'sources', 'transformations').
  by(valueMap(true)).
  by(
    repeat(inE().outV().simplePath()).
    until(hasLabel('source_asset')).
    dedup().
    valueMap(true).
    fold()
  ).
  by(
    repeat(inE().outV().simplePath()).
    until(hasLabel('source_asset')).
    path().
    by(valueMap('type', 'transformation_details')).
    fold()
  )

// Option 4: Group sources by transformation paths
g.V().
  hasLabel('asset').
  has('id', 'consumer-asset-id').
  union(
    identity().valueMap(true),
    repeat(inE().outV().simplePath()).
    until(hasLabel('source_asset')).
    group().
    by(path().count()).  // Group by path length
    by(
      group().
      by('type').  // Group by asset type
      by(valueMap(true).fold())
    )
  )

// Option 5: Shortest paths to source assets with transformation metadata
g.V().
  hasLabel('asset').
  has('id', 'consumer-asset-id').
  project('consumer', 'paths').
  by(valueMap(true)).
  by(
    repeat(inE().outV()).
    until(
      or(
        hasLabel('source_asset'),
        loops().is(gte(10))
      )
    ).
    path().
    by(
      choose(
        hasLabel('transformation'),
        valueMap('type', 'transformation_details'),
        valueMap(true)
      )
    ).
    limit(10)  // Limit number of paths
  )

```

Key features of these queries:

1. Depth Control:
    - Uses `loops().is(gte(10))` to prevent infinite traversals
    - Implements `simplePath()` to avoid cycles

2. Performance Optimizations:
    - Uses `project()` for structured output
    - Implements batching with `fold()`
    - Includes property filtering in `valueMap()`

3. Data Quality:
    - Captures transformation metadata
    - Preserves path information
    - Groups results by meaningful criteria

To use these queries:

1. Replace 'consumer-asset-id' with your actual consumer asset identifier
2. Adjust property names ('type', 'name', etc.) to match your schema
3. Modify edge labels if different
4. Adjust the max depth (10) based on your known transformation layers

Tips for Neptune optimization:

1. Add `.with(Neptune.QUERY_TIMEOUT, 180000)` for long-running queries
2. Use `.profile()` to analyze performance
3. Consider adding indices on frequently queried properties
4. Use `valueMap(true)` instead of `elementMap()`