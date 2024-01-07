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

# Function to execute Gremlin queries
def execute_gremlin_query(query):
    # Connect to your Gremlin Server
    remoteConn = DriverRemoteConnection(f'ws://{neptune_host}:{neptune_port}/gremlin', 'g')
    g = traversal().withRemote(remoteConn)
    results = eval(query)
    return results

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form.get("query")
        results = execute_gremlin_query(query)
        # Process the results (you can customize this part)
        # processed_results = []  # Store processed results here
        #
        # for result in results:
        #     processed_result = {
        #         'id': result['id'],
        #         'label': result['label'],
        #         'properties': result['properties']
        #     }
        # processed_results.append(processed_result)
        #
        # # Convert processed results to JSON
        # json_results = jsonify(processed_results)
        # return json_results

        # You can process and render the result as an image here
        # For simplicity, we'll just convert it to JSON
        return jsonify(results)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
