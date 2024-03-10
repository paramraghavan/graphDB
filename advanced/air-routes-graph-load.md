# Load Air Routes
- start tinkerpop gremlin console
- Clean up the graph database if need
```gremlin
g.V().drop().iterate()
```
- load graph ml  data
```gremlin
 graph.io(graphml()).readGraph('/Users/paramraghavan/dev/tinkerpop/advanced/air-routes.graphml')
```