# Key points about pagination in Neptune:
The primary way to handle pagination in Gremlin is using `range()` step.

```groovy
// Basic pagination (items 0-9)
g.V().range(0, 10)

// Skip first 10, get next 10 (items 10-19)
g.V().range(10, 20)

// With label filter
g.V().hasLabel('person').range(0, 10)

// With property filter and sorting
g.V().hasLabel('person')
     .has('age', gt(25))
     .order().by('name')
     .range(0, 10)

// Count total results
g.V().hasLabel('person').count()

```

- Use `range(start, end)` for pagination
- Always place `range()` after your filters to ensure correct pagination
- Remember that `range()` is zero-based
- Calculate total count separately to provide proper pagination metadata
