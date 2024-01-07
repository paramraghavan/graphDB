from flask import Flask, request, render_template, jsonify
from gremlin_python.driver import client, serializer
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64

from flask import Flask, render_template, request, jsonify
from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver import client
from gremlin_python.driver import serializer
from gremlin_python.process.traversal import T
from gremlin_python.process.graph_traversal import __


app = Flask(__name__)

# Define the Neptune server connection configuration
neptune_host = "localhost"
neptune_port = 8182


@app.route('/')
def index():
    return render_template('index_graph.html')


@app.route('/query', methods=['POST'])
def query_tinkerpop():
    query_data = request.get_json()
    user_query = query_data['query']

    remoteConn = DriverRemoteConnection(f'ws://{neptune_host}:{neptune_port}/gremlin', 'g')
    g = traversal().withRemote(remoteConn)
    results = eval(user_query)

    # Create a NetworkX graph to represent the data (sample)
    G = nx.Graph()
    for result in results:
        if 'id' in result:
            # If the result has an 'id' property, it's a vertex
            vertex_id = result['id']
            G.add_node(vertex_id, **result)  # Add the vertex to the graph
        elif 'outV' in result and 'inV' in result:
            # If the result has 'outV' and 'inV' properties, it's an edge
            source_vertex_id = result['outV']
            destination_vertex_id = result['inV']
            edge_id = result['id']  # You can use 'id' as the edge identifier
            G.add_edge(source_vertex_id, destination_vertex_id, id=edge_id, **result)  # Add the edge to the graph


    # Visualize the graph (sample)
    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 10))
    nx.draw(G, pos, with_labels=True, node_size=1000, node_color='skyblue', font_size=8)

    # Save the plot as an image
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)
    img_base64 = base64.b64encode(img_data.read()).decode('utf-8')

    return jsonify({'image': img_base64})


if __name__ == '__main__':
    app.run(debug=True)
