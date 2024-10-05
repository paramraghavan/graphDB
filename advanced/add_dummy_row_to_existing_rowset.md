# Adding a dummy row to the query
I am using to add default value to the UI selection


```gremlin
.union(
  identity(),
  constant(1).project('id', 'label', 'properties')
    .by(constant('dummy_id'))
    .by(constant('Dummy Row'))
    .by(constant(['value': [0]]))
)

```

# updating existing query and adding a dummy row
Adding dummy row and ordering the resultset by name, defaults to ascending.

```gremlin
// Correct syntax for union and inject in Neptune Gremlin
g.V().hasLabel('someLabel')
  .project('id', 'name', 'value')
    .by(id)
    .by('name')
    .by('value')
.union(
  identity(),
  constant(1).project('id', 'name', 'value')
    .by(constant('dummy_id'))
    .by(constant('Dummy Row'))
    .by(constant(['value': [0]]))
)
.order()
.by('name')

```

