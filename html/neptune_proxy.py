from flask import Flask, request, jsonify
from flask import Flask, render_template, request

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __, elementMap, bothE
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal

app = Flask(__name__)
# Define the Neptune server connection configuration
neptune_host = "localhost"
neptune_port = 8182

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query_graph():
    query = request.form["query"]
    graph = Graph()
    remoteConn = DriverRemoteConnection(f'ws://{neptune_host}:{neptune_port}/gremlin', 'g')
    g = traversal().withRemote(remoteConn)
    user_query = 'g.V().repeat(bothE().otherV()).times(2).path().by(__.elementMap())'
    results = eval(user_query)
    results = g.V().repeat(bothE().otherV()).times(2).path().by(__.elementMap()).toList()  # Replace with actual query logic
    for path in results:
        print(path)  # This iterates over the returned results and prints them.
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
