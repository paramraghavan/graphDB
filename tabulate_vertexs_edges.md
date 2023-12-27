# gremlin how to list all the vertexs abd edges in tablular format

Gremlin itself doesn't inherently support a "table" structure like SQL, you would typically format the results into a table-like structure in your application code after retrieving the data. However, you can structure your query to make this post-processing as straightforward as possible.

## Listing All Vertices
```groovy
# This query will return a list of maps, where each map represents
# a vertex with its id, label, and a map of its properties (properties).
g.V().project('id', 'label', 'properties')
     .by(T.id)
     .by(T.label)
     .by(valueMap())
     .toList()

```

## Listing All Edges
```groovy

# This query will return a list of maps, where each map represents an edge with its id,
# label, outV (outgoing vertex ID), inV (incoming vertex ID), 
# and a map of its properties (properties).

g.E().project('id', 'label', 'outV', 'inV', 'properties')
     .by(T.id)
     .by(T.label)
     .by(outV().id())
     .by(inV().id())
     .by(valueMap())
     .toList()
```

# Tablular format using python + pandas 
```python
import pandas as pd

# Assume vertices and edges are the result of the Gremlin queries above
vertices = g.V().project('id', 'label', 'properties')
edges = g.E().project('id', 'label', 'outV', 'inV', 'properties')

# Convert to DataFrames
vertices_df = pd.DataFrame(vertices)
edges_df = pd.DataFrame(edges)

# Now you can display these DataFrames as tables
print(vertices_df)
print(edges_df)

```