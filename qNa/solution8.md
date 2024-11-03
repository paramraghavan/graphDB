# The query modified to add a new property to 'to-result' edge based on the result's status.
**Here's the updated query:**

```groovy
g.V().
  hasLabel('ruleset').
  repeat(
    outE('to-rule').
    inV().
    hasLabel('rule').
    coalesce(
      outE('to-result').
      as('resultEdge').      // Label the edge for later reference
      inV().
      hasLabel('result').
      order().by('created_timestamp', desc).
      limit(1).
      choose(values('status').is('passed'),
        // If status is 'passed'
        __.select('resultEdge')
          .property('execution_status', 'passed'),
        // If status is 'failed'
        __.select('resultEdge')
          .property('execution_status', 'failed')
      ),
      identity()
    )
  ).
  emit().
  path().
  by(elementMap())
```

- Alternative approach using sideEffect:

```groovy
g.V().
  hasLabel('ruleset').
  repeat(
    outE('to-rule').
    inV().
    hasLabel('rule').
    coalesce(
      outE('to-result').
      as('resultEdge').
      inV().
      hasLabel('result').
      order().by('created_timestamp', desc).
      limit(1).
      sideEffect(
        select('resultEdge')
          .property('execution_status', 
            choose(values('status').is('passed'),
              constant('passed'),
              constant('failed')
            )
          )
      ),
      identity()
    )
  ).
  emit().
  path().
  by(elementMap())
```

Key changes explained:

1. Added `as('resultEdge')` to store reference to the edge
2. Used `choose()` to check result status:
   ```groovy
   choose(values('status').is('passed'),
     // If true (passed)
     __.select('resultEdge').property('execution_status', 'passed'),
     // If false (failed)
     __.select('resultEdge').property('execution_status', 'failed')
   )
   ```

If you need to handle more status values:

```groovy
g.V().
  hasLabel('ruleset').
  repeat(
    outE('to-rule').
    inV().
    hasLabel('rule').
    coalesce(
      outE('to-result').
      as('resultEdge').
      inV().
      hasLabel('result').
      order().by('created_timestamp', desc).
      limit(1).
      sideEffect(
        select('resultEdge')
          .property('execution_status', 
            choose(values('status'))
              .option('passed', 'passed')
              .option('failed', 'failed')
              .option('error', 'failed')
              .option(none, 'unknown')
          )
      ),
      identity()
    )
  ).
  emit().
  path().
  by(elementMap())
```

This will:
1. Find the latest result for each rule
2. Read the result's status property
3. Add a new 'execution_status' property to the to-result edge
4. Include the updated edge properties in the path output
