from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
import csv
from gremlin_python.process.traversal import T
import random
"""
# miles in the routes file are some random number
"""
# Connect to your Gremlin Server
graph = Graph()
remoteConn = DriverRemoteConnection('ws://localhost:8182/gremlin','g')
g = graph.traversal().withRemote(remoteConn)

"""
With In memory TinkerGraph, you can use Long data type as an identifier for a vertex and edge
"""
# Function to load airports
def load_airports(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        vertex_id = 40000
        for row in reader:
            vertex_id = vertex_id + 1
            g.addV('airport').property(T.id, vertex_id).property('code', row['code']).property('name', row['name']).next()

# Function to load routes
def load_routes(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        edge_id = 50000
        for row in reader:
            edge_id = edge_id + 1
            from_airport = g.V().has('airport', 'code', row['from']).next()
            to_airport = g.V().has('airport', 'code', row['to']).next()
            g.V(from_airport).addE('route').property(T.id, edge_id).to(to_airport).property('miles', int(row['miles'])).iterate()

# Load airports and routes
load_airports('./airports.csv')
# miles in the routes file are some random number
load_routes('./routes.csv')

# Close the connection
remoteConn.close()
