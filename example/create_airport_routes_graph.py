from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
import csv
from gremlin_python.process.traversal import T
import random

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
        for row in reader:
            g.addV('airport').property(T.id, random.randint(100,10000)).property('code', row['code']).property('name', row['name']).next()

# Function to load routes
def load_routes(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            from_airport = g.V().has('airport', 'code', row['from']).next()
            to_airport = g.V().has('airport', 'code', row['to']).next()
            g.V(from_airport).addE('route').property(T.id, random.randint(21000,30000)).to(to_airport).property('miles', int(row['miles'])).iterate()

# Load airports and routes
load_airports('./airports.csv')
load_routes('./routes.csv')

# Close the connection
remoteConn.close()
