# create a graph airport and filter all the routes for given start and endpoint 
- write python code using tinkerpop, gremlin
- Create a Graph and Add Data 
```python
from gremlin_python import statics
from gremlin_python.structure.io.graphsonV3d0 import GraphSONReader
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal

# Connect to Gremlin Server
g = traversal().withRemote(DriverRemoteConnection('ws://localhost:8182/gremlin', 'g'))

# Create airports
g.addV('airport').property('code', 'LAX').property('name', 'Los Angeles International Airport').iterate()
g.addV('airport').property('code', 'JFK').property('name', 'John F. Kennedy International Airport').iterate()
g.addV('airport').property('code', 'ATL').property('name', 'Hartsfield-Jackson Atlanta International Airport').iterate()

# Create routes
g.V().has('airport', 'code', 'LAX').as_('lax').V().has('airport', 'code', 'JFK').addE('route').from_('lax').property('distance', 2475).iterate()
g.V().has('airport', 'code', 'LAX').as_('lax').V().has('airport', 'code', 'ATL').addE('route').from_('lax').property('distance', 1946).iterate()

```
- Filter Routes and Write to File
```python
def find_routes(start_code, end_code):
    routes = g.V().has('airport', 'code', start_code) \
                 .outE('route') \
                 .inV().has('code', end_code) \
                 .path().by('name').by('distance') \
                 .toList()
    return routes

# Example: Find routes from LAX to JFK
routes = find_routes('LAX', 'JFK')

# Writing results to a file
with open('routes.txt', 'w') as file:
    for route in routes:
        file.write(str(route) + '\n')

print("Routes written to routes.txt")

```

