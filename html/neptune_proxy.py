from flask import Flask, request, jsonify
from flask import Flask, render_template, request

from gremlin_python import statics
from gremlin_python.structure.graph import Graph, Vertex, Edge
from gremlin_python.process.graph_traversal import __, elementMap, bothE
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.traversal import T, Direction

app = Flask(__name__)
# Define the Neptune server connection configuration
neptune_host = "localhost"
neptune_port = 8182

@app.route('/')
def index():
    return render_template('index.html')
import json

@app.route('/query', methods=['POST'])
def query_graph():
    query = request.form["query"]
    graph = Graph()
    remoteConn = DriverRemoteConnection(f'ws://{neptune_host}:{neptune_port}/gremlin', 'g')
    g = traversal().withRemote(remoteConn)
    user_query = 'g.V().repeat(bothE().otherV()).times(2).path().by(__.elementMap())'
    # results = eval(user_query)
    results = g.V().repeat(bothE().otherV()).times(2).path().by(__.elementMap()).toList()  # Replace with actual query logic
    # Convert paths to a JSON serializable list
    json_paths = [path_to_dict(path) for path in results]

    return json_paths

def path_to_dict(path):
    return [element_to_dict(element) for element in path]

def element_to_dict(element):
    if isinstance(element, dict):
        # Convert keys and values in the dictionary
        return {str(k) if isinstance(k, (T,Direction)) else k: element_to_dict(v) for k, v in element.items()}
    elif isinstance(element, list):
        # Convert each element in the list
        return [element_to_dict(e) for e in element]
    elif hasattr(element, 'id') and hasattr(element, 'label'):
        # Handling for Vertex and Edge objects
        return {"type": "vertex" if isinstance(element, Vertex) else "edge",
                "id": element.id, "label": element.label,
                "properties": element_to_dict(element.properties)}
    else:
        return element


if __name__ == '__main__':
    app.run(debug=True)
