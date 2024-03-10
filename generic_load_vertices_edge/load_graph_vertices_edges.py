from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from generic_load_vertices_edge.parse_vertices_edges import load_graph_from_yaml
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __

# Define the Neptune server connection configuration
neptune_host = "localhost"
neptune_port = 8182

"""
Note the miles between routes are some random value
"""

# Connect to your Gremlin Server
graph = Graph()
remoteConn = DriverRemoteConnection(f'ws://{neptune_host}:{neptune_port}/gremlin','g')
#g = graph.traversal().withRemote(remoteConn)
g = traversal().withRemote(remoteConn)


vertices, edges, id_map = load_graph_from_yaml('data.yaml')
"""
# Adding vertices with properties
for vertex in vertices:
    v = g.addV(vertex['label']).property('id', id_map[vertex['id']])
    for prop, value in vertex['properties'].items():
        v.property(prop, value)
    v.next()

'''
- Assumption: The vertex IDs (edge['from'] and edge['to']) already exist in the graph.
- We use __.V(edge['to']) for specifying the target vertex in an edge creation. __ represents an anonymous traversal, 
which is the correct way to define a traversal inside another traversal (like within an addE() step).
- also added g.iterate() at the end of the edge-adding loop, which is necessary to actually 
execute the traversal.
'''

# Adding edges
for edge in edges:
    e = g.V(id_map[edge['from']]).addE(edge['label']).to(__.V(id_map[edge['to']]))
    for prop, value in edge.get('properties', {}).items():
        e.property(prop, value)
    e.iterate()

# Don't forget to close the connection
remoteConn.close()
"""

# Function to add a vertex if it doesn't exist
def add_vertex_if_not_exists(g, vertex):
    if not g.V().has('id', id_map[vertex['id']]).hasNext():
        v = g.addV(vertex['label']).property('id', id_map[vertex['id']])
        for prop, value in vertex['properties'].items():
            v.property(prop, value)
        v.next()
    else:
        print(f'vertex already exists: {vertex}')

# Function to add an edge if it doesn't exist
def add_edge_if_not_exists(g, edge):
    if not g.V().has('id',id_map[edge['from']]).out(edge['label']).has('id', id_map[edge['to']]).hasNext():
        e = g.V().has('id',id_map[edge['from']]).addE(edge['label']).to(__.V().has('id', id_map[edge['to']]))
        for prop, value in edge.get('properties', {}).items():
             e.property(prop, value)
        e.iterate()
    else:
        print(f'edge already exists: {edge}')

# Adding vertices and edges
for vertex in vertices:
    add_vertex_if_not_exists(g, vertex)

for edge in edges:
    add_edge_if_not_exists(g, edge)

# Don't forget to close the connection
remoteConn.close()

