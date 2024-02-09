from flask import Flask, request, jsonify
from flask import Flask, render_template, request

from gremlin_python import statics
from gremlin_python.structure.graph import Graph, Vertex, Edge
from gremlin_python.process.graph_traversal import __, elementMap, bothE
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.traversal import T, Direction
from gremlin_python.driver import client, serializer

app = Flask(__name__)
# Define the Neptune server connection configuration
neptune_host = "localhost"
neptune_port = 8182

graph = Graph()
remoteConn = DriverRemoteConnection(f'ws://{neptune_host}:{neptune_port}/gremlin', 'g')
g = traversal().withRemote(remoteConn)


@app.route('/')
def index():
    return render_template('index.html')
import json

#  https://aiogremlin.readthedocs.io/en/latest/index.html
@app.route('/query', methods=['POST'])
def query_graph():
    query = request.form["query"]

    #user_query = 'g.V().repeat(bothE().otherV()).times(2).path().by(elementMap())' #'g.V().repeat(bothE().otherV()).times(2).path().by(__.elementMap())'
    # g.V().repeat(out()).times(3).path().by(elementMap())
    # results = eval(user_query)
    # user_query = "g.V().outE().inV().project('source', 'target', 'edgeProperty').by(id()).by(out()).by('property').path()"
    #user_query = 'g.V().repeat(bothE().otherV()).times(2).path().by(elementMap()).toList()'
    user_query = 'g.with_("evaluationTimeout", 90000).V().repeat(__.outE().inV()).times(1).limit(3).dedup().path().by(__.elementMap()).toList()'
    # Assuming g is your traversal source as defined earlier
    # This example just shows how to set options, replace the actual traversal according to your needs

    results = eval(user_query)
    # Replace with actual query logic
    # Convert paths to a JSON serializable list
    #json_paths = [path_to_dict(path) for path in results]
    nodes, edges = parse_path(results)

    nodes_edges = {}
    nodes_edges['nodes'] = nodes
    nodes_edges['edges'] = edges
    json_result = json.dumps(nodes_edges)
    return json_result


def parse_path(paths) ->([],[]):
    # color node based on 'code'
    color_prop = 'code'
    nodes = []
    edges = []
    id_list = []
    for path in paths:
        for element in path:
           # {str(k) if isinstance(k, (T,Direction)) else k: element_to_dict(v) for k, v in element.items()}
            elm = {}
            for k, v in element.items():
                if isinstance(k, (T)):
                    if 'id' in str(k):
                        elm['id'] = v
                    if 'label' in str(k):
                        elm['label'] = v
                elif isinstance(k, Direction):
                    if 'IN' in str(k):
                        elm['target'] = next(iter(v.values())) # or use list(v.values())[0]
                    if 'OUT' in str(k):
                        elm['source'] = next(iter(v.values()))
                else:
                    elm[k] = v
            if 'vertex' in elm['label']:
                if elm['id'] not in id_list:
                    id_list.append(elm['id'])
                    if color_prop in elm.keys():
                       color =  string_to_color_code(elm[color_prop])
                    else:
                        color = '#000000'
                    elm['color']  = color
                    nodes.append(elm)
            else:
                elm['width'] = 2
                edges.append(elm)
    return (nodes, edges)


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


import hashlib


def string_to_color_code(s):
    # Use a hash function (e.g., MD5) to get a consistent hash value
    hash_object = hashlib.md5(s.encode())
    # Take the first 6 characters from the hash's hexadecimal representation
    hex_digest = hash_object.hexdigest()[:6]

    # Convert the hex digest into an integer
    color_int = int(hex_digest, 16)

    # Ensure the color is in the range from #800000 to #FFFFFF
    # Adjust the range to start from 0x800000
    min_color = 0x800000
    max_color = 0xFFFFFF
    adjusted_color_int = min_color + (color_int % (max_color - min_color + 1))

    # Convert back to hex, removing the '0x' prefix and ensuring it's 6 characters long
    adjusted_color_hex = f'#{adjusted_color_int:06X}'

    return adjusted_color_hex



if __name__ == '__main__':
    app.run(debug=True)
