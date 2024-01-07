import networkx as nx
import matplotlib.pyplot as plt
from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import T

# Define the Neptune server connection configuration
neptune_host = "localhost"
neptune_port = 8182


# Connect to your Gremlin Server
graph = Graph()
remoteConn = DriverRemoteConnection(f'ws://{neptune_host}:{neptune_port}/gremlin','g')
g = graph.traversal().withRemote(remoteConn)

# Execute a Gremlin query to retrieve airports and routes data
# results = g.V().hasLabel('airport').valueMap().toList()

results = g.V().project('id', 'label', 'properties')\
              .by(T.id)\
              .by(T.label)\
              .by(__.valueMap())\
              .toList()
print(results)

# Create a NetworkX graph to represent the data
G = nx.Graph()

# Add airports as nodes
for result in results:
    airport_id = result['id']
    airport_name = result['properties']['name'][0]
    G.add_node(airport_id, name=airport_name, label=airport_name)


# Execute a Gremlin query to retrieve routes data
# query = "g.E().hasLabel('route').valueMap().toList()"
# results = g.submit(query).all().result()
results = g.E().project('id', 'label', 'outV', 'inV', 'properties')\
     .by(T.id)\
     .by(T.label)\
     .by(__.outV().id())\
     .by(__.inV().id())\
     .by(__.valueMap())\
     .toList()

# Add routes as edges
for result in results:
    source_airport_id = result['outV']
    destination_airport_id = result['inV']
    G.add_edge(source_airport_id, destination_airport_id)

# Visualize the graph
pos = nx.spring_layout(G)
plt.figure(figsize=(10, 10))
nx.draw(G, pos, with_labels=True, node_size=1000, node_color='skyblue', font_size=8)
# Drawing labels on the nodes
# The labels parameter should be a dictionary mapping node names to labels
# If you want to use default labels (which are node names), you can do this:
for item in G.nodes.data():
    print(item[0], item[1]['name'])
labels = {item[0]: item[1]['name'] for node in G.nodes.data()}
nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
plt.title('Airport Routes Graph')
plt.show()
