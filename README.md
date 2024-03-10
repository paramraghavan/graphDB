# What is GraphDB

A graph database is a type of database that uses graph structures for semantic queries with nodes, edges, and properties
to represent and store data. It is designed to handle data whose relationships are as important as the data itself.
Popular graphdbs - Neo4j, AWS Neptune, ArangoDB, etc... Is tinkerpop a graphdb? We will be using Tinkerpop on localhost 
and AWS Neptune.

# What is Tinkerpop
Apache TinkerPop is an open-source project providing a framework and a set of tools to unify different graph
technologies under a common framework and language has made it a cornerstone in the field of graph computing. TinkerPop
defines both a graph computing framework and a query language called Gremlin.

- Implementation: It is **not a database itself** but provides a set of tools and APIs (like Gremlin) for building and
  querying graph databases.
- Compatibility: TinkerPop is designed to be compatible with various graph databases, including Neo4j, Apache Cassandra,
  and more.
- Features: It offers a standard way to interact with graph databases, regardless of the underlying database
  implementation.
- Use Cases: TinkerPop is used by developers to build and query graph databases in a consistent manner across different
  database systems.
> TinkerPop supports Cypher through an extension called Gremlin-Cypher. It is important to note that the support for
> Cypher in TinkerPop might not be as extensive or optimized as in Neo4j, where Cypher is the native query language.

# Why Graph database
Here are the 3 main reasons:
* **Efficient Relationship Processing**: Graph databases are designed to handle interconnected data. They excel in managing relationships 
between data points, making them ideal for use cases where relationships are as important as the data itself. For example, social networks,
recommendation engines, and fraud detection systems heavily rely on the relationships between various entities. In a graph database, 
traversing these relationships is much faster and more efficient than in traditional relational databases.
* **Direct Representation of Relationships**: In graph databases, an edge is a direct and explicit representation of a relationship between two nodes. 
This means that each connection or relation is its own entity, often with its own properties and attributes. For instance, in a social network graph, 
an edge might not only connect two people (nodes) but also carry information like the type of relationship (“friend,” “colleague”) and the date it was established.
* **Flexibility in Evolving Schemas**: Graph databases typically don’t require a fixed schema, meaning they are more adaptable to changes 
in data structures. This flexibility is beneficial in scenarios where data and relationships are constantly evolving, such as in 
content management systems or in scenarios involving unstructured data. This schema-less nature allows for easier integration of new
types of data and relationships without the need for extensive database redesign.
>The first-class nature of edges allows for more flexibility in data modeling. Relationships are not confined to rigid table structures and can evolve over time
  without the need for significant schema changes, which is often a limitation in relational databases relying on foreign keys.
* **Intuitive Data Modeling and Visualization**: The graph model is often more intuitive for representing complex relationships and networks 
of data. This can make it easier for developers and data scientists to model and visualize complex structures, like supply chains or network 
topologies. Graph databases can help in understanding these structures more deeply and in identifying patterns and insights that might be 
less apparent in traditional tabular data representations.
* **Attributes and Properties**: Unlike foreign keys in relational databases, which primarily serve as references or links between tables, edges in graph databases 
can hold various attributes. This allows for more nuanced and detailed descriptions of the relationships between nodes

In graph databases, edges are treated as “first-class citizens,” which means they are given as much importance and functionality as other elements like nodes or vertices. 
This contrasts with how relationships are typically handled in relational databases, where they are often represented indirectly through foreign keys.

**Summary:**
Graph databases are ideal for scenarios where relationships are key, data is highly connected, schema flexibility is required, and where quick navigation through
complex networks is essential. However, for applications with simpler, less interconnected data, or where the primary need is to store large volumes of data with 
simple retrieval, traditional relational databases or other NoSQL databases might be more suitable.

**Learning Path:** 
- [Thinking In Gremlin](thinking_in_graph.md)
- [Graph Use Cases](graph_usecases%2FREADME.md)


# Installing Apache TinkerPop on a Mac
- TinkerPop requires Java to be installed on your system. You can check if Java is already installed and what version it is by running
```shell
brew install openjdk@17 # use jdk 17. Tinker pop 3.7.1 supports Java8,Java 11 and Java17
```
- Download the TinkerPop Binary: Go to the [Apache TinkerPop download](https://tinkerpop.apache.org/download.html) page and download the latest binary release
- https://www.apache.org/dyn/closer.lua/tinkerpop/3.7.1/apache-tinkerpop-gremlin-console-3.7.1-bin.zip
- Unzip the Downloaded File: Once the download is complete, unzip the file in your desired directory and start gremlin console
```shell
cd apache-tinkerpop-gremlin-console-*/
bin/gremlin.sh
```
- Gremlin server
  - https://dlcdn.apache.org/tinkerpop/3.7.1/apache-tinkerpop-gremlin-server-3.7.1-bin.zip
  - apache-tinkerpop-gremlin-server-3.7.1/bin/gremlin-server.sh start

## Tutorial
- https://www.kelvinlawrence.net/book/PracticalGremlin.html
- [Gremlin CheatSheet](https://dkuppitz.github.io/gremlin-cheat-sheet/101.html)

# Gremlin
You can get a list of the available commands by typing :help. Note that all commands to the console itself are prefixed by a colon ":". This enables the
console to distinguish them as special and different from actual Gremlin and Groovy commands.
```groovy
gremlin> :help
Available commands:
  :help       (:h  ) Display this help message
  ?           (:?  ) Alias to: :help
  :exit       (:x  ) Exit the shell
  :quit       (:q  ) Alias to: :exit
  :import      (:i  ) Import a class into the namespace
  :display    (:d  ) Display the current buffer
  :clear      (:c  ) Clear the buffer and reset the prompt counter
  :show       (:S  ) Show variables, classes or imports
  :inspect    (:n  ) Inspect a variable or the last result with the GUI object browser
  :purge      (:p  ) Purge variables, classes, imports or preferences
  :edit       (:e  ) Edit the current buffer
  :load       (:l  ) Load a file or URL into the buffer
  .           (:.  ) Alias to: :load
  :save       (:s  ) Save the current buffer to a file
  :record     (:r  ) Record the current session to a file
  :history    (:H  ) Display, manage and recall edit-line history
  :alias      (:a  ) Create an alias
  :grab       (:g  ) Add a dependency to the shell environment
  :register   (:rc ) Register a new command with the shell
  :doc        (:D  ) Open a browser window displaying the doc for the argument
  :set        (:=  ) Set (or list) preferences
  :uninstall  (:-  ) Uninstall a Maven library and its dependencies from the Gremlin Console
  :install    (:+  ) Install a Maven library and its dependencies into the Gremlin Console
  :plugin     (:pin) Manage plugins for the Console
  :remote     (:rem) Define a remote connection
  :submit     (:>  ) Send a Gremlin script to Gremlin Server
  :bytecode   (:bc ) Gremlin bytecode helper commands
  :cls        (:C  ) Clear the screen.
```
> Of all the commands listed above :clear (:c for short) is an important one to remember. If the console starts acting strangely or you find yourself stuck with a prompt like "…​…​1>" , typing :clear will reset things nicely.

It is worth noting that as mentioned above, the Gremlin console is based on the Groovy console and as such you can enter valid Groovy code directly into the console. So as well as using it to experiment with Graphs and Gremlin you can use it as, for example, a desktop calculator should you so desire!

```groovy
gremlin> 2+3
==>5

gremlin> a = 5
==>5

gremlin> println "The number is ${a}"
The number is 5

gremlin> for (a in 1..5) {print "${a} "};println()
1 2 3 4 5
```


## Gremlin version
```groovy
// What version of Gremlin console am I running?
gremlin>  Gremlin.version()
==>3.4.10
```

## Saving output from the console to a file
```groovy
gremlin> :record start mylog.txt
Recording session to: "mylog.txt"

gremlin> g.V().count().next()
==>3618
gremlin> :record stop
Recording stopped; session saved as: "mylog.txt" (157 bytes)
```

## TinkerGraph
As well as the Gremlin Console, the TinkerPop 3 download includes an implementation of an in-memory graph store called TinkerGraph.
The nice thing about TinkerGraph is that for learning and testing things you can run everything you need on your laptop or desktop computer and be up and running very quickly

- When running in the Gremlin Console, support for TinkerGraph should be on by default. If for any reason you find it to be off you, can enable it by issuing the following command.
  ```groovy
  gremlin>:plugin use tinkerpop.tinkergraph
  ```
- Once the TinkerGraph plugin is enabled you will need to close and re-load the Gremlin console. After doing that, you can create a new TinkerGraph instance from the console as follows.
  ```groovy
  gremlin>graph = TinkerGraph.open()
  // Before you can start to issue Gremlin queries against the graph you also need to establish a graph traversal
  // source object by calling the new graph’s traversal method as follows. The variable name graph will be used
  // for any object that represents a graph instance and the variable name g will be used for any object that
  // represents an instance of a graph traversal source object.
  gremlin>g = graph.traversal()
  gremlin>graph.features()
  ```

## conf/remote.yaml file on the console side
```yaml
hosts: [localhost]
port: 8182
serializer: { className: org.apache.tinkerpop.gremlin.util.ser.GraphBinaryMessageSerializerV1, config: { serializeResultToString: true }}
```

## How to connect to gremlin server from gremlin console
- start the Gremlin server
- start the Gremlin console
### Connect to the Gremlin Server from console
- Once the Gremlin Console is open, you can connect to your Gremlin Server using the :remote command followed by the connect command. The default Gremlin Server connection alias is usually g.
```groovy
:remote connect tinkerpop.server conf/remote.yaml
:remote console
# increase timeout
:remote config timeout 3000000 
Also see --> https://aiogremlin.readthedocs.io/en/latest/index.html

```
- conf/remote.yaml is the configuration file for the remote connection. This file should be present in your Gremlin
  Console's directory. It contains the details about how to connect to the Gremlin Server, including the host and port.
- Issue gremlin commands on gremlin console
- When you want to run Gremlin queries on a graph database that is not hosted locally, but on a remote server, you use
  the **:remote console** command to route your queries to that server.
  
```groovy
g.V().count() // 6
// show vertex labels and properties
g.V().valueMap().with(WithOptions.tokens)

Above query breaks down as follows:
- g.V(): This starts a traversal at all vertices in the graph.
- valueMap(): This fetches the properties of each vertex.
- with(WithOptions.tokens): This includes the vertex's ID and label in the output.

//Result:
//==>{id=0, label=account, accountId=[A1], holderName=[John Doe], balance=[10000]}
//==>{id=18, label=transaction, amount=[1500], transactionId=[T3]}
//==>{id=4, label=account, accountId=[A2], holderName=[Jane Smith], balance=[5000]}
//==>{id=8, label=account, accountId=[A3], holderName=[Alice Johnson], balance=[7000]}
//==>{id=12, label=transaction, amount=[2000], transactionId=[T1]}
//==>{id=15, label=transaction, amount=[3000], transactionId=[T2]}

```
## aiogremlin
aiogremlin is an asynchronous DSL based on the official Gremlin-Python
- https://aiogremlin.readthedocs.io/en/latest/index.html

## Steps to Visualize Graph from TinkerPop Server using Gephi:
- Step 1: Export Graph Data from TinkerPop Server
- First, you'll need to extract your graph data (vertices and edges) from the TinkerPop server. Use Gremlin queries to retrieve this data and export it into a format like GraphML or GEXF. For example:
```groovy
// Example Gremlin query to write graph to GraphML
g.io('/path/to/graph.graphml').write().iterate()
```  
- Step 2: Install Gephi or Cytoscape
- If you don't have Gephi installed, you can download it from the Gephi website - https://gephi.org/users/download/.  

## explain plan - explain()
The explain() step is used to provide a detailed explanation of the traversal strategy and the optimizations applied by the query planner. This is particularly useful for understanding how a given Gremlin query will be executed, which can help in optimizing and debugging your queries.

```groovy
g.V().has('person', 'name', 'Alice').out('friends').values('name').explain()
```
This query does the following:
* g.V(): Start from all vertices.
* .has('person', 'name', 'Alice'): Filter vertices to find those that have a label 'person' and a property 'name' with the value 'Alice'.
* .out('friends'): Traverse to the outgoing 'friends' edges.
* .values('name'): Extract the 'name' property of these friend vertices.
* explain
  * shows steps of the traversal.
  * Optimization strategies used (e.g., filter optimization, index usage).
  * The order in which steps are executed, which might differ from the order in which they are written due to optimizations.

## Neptune multiple label support
Neptune supports multiple labels for a vertex. When you create a label, you can specify multiple labels by separating them with ;;. 
For example, g.addV("Label1;;Label2;;Label3") adds a vertex with three different labels. The hasLabel step matches this vertex 
with any of those three labels: hasLabel("Label1"), hasLabel("Label2"), and hasLabel("Label3").

>> The ;; delimiter is reserved for this use only. You cannot specify multiple labels in the hasLabel step.<br>
> For example, hasLabel("Label1;;Label2") does not match anything.<br>
> It is best practice to use single label as multiple labels are not supported in all graph platform<br>
> Gremlin cannot delete labels. you can delete labels using openCypher, but at least one label has to be left.

ref: https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-differences.html

## Setup python neptune environment
- [Setup Env for Neptune](./graph-notebook/README.md)

## Useful links
- https://github.com/aws/graph-notebook
- https://github.com/aws/graph-notebook.git
- https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-differences.html

## Neptune resources
- https://aws.amazon.com/neptune/developer-resources/
- https://github.com/awslabs/amazon-neptune-tools