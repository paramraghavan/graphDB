# pip install networkx matplotlib

import networkx as nx
import matplotlib.pyplot as plt

# Create a new graph
G = nx.Graph()

# Add nodes
G.add_node("A")
G.add_node("B")
G.add_node("C")

# Add edges
G.add_edge("A", "B")
G.add_edge("B", "C")
G.add_edge("C", "A")

# You can also add nodes and edges together like
# G.add_edges_from([("A", "B"), ("B", "C"), ("C", "A")])

# Draw the graph
nx.draw(G, with_labels=True, node_color='lightblue', edge_color='gray')

# Display the plot
plt.show()
