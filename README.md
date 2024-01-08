# What is Tinkerpop
Apache TinkerPop is an open-source project providing a framework and a set of tools to unify different graph technologies under a common framework and language has made it a cornerstone in the field of graph computing. TinkerPop defines both a graph computing framework and a query language called Gremlin.


# Installing Apache TinkerPop on a Mac
- TinkerPop requires Java to be installed on your system. You can check if Java is already installed and what version it is by running
```shell
brew install openjdk
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
```
- conf/remote.yaml is the configuration file for the remote connection. This file should be present in your Gremlin Console's directory. It contains the details about how to connect to the Gremlin Server, including the host and port.
- Issue gremlin commands on gremlin console
- When you want to run Gremlin queries on a graph database that is not hosted locally, but on a remote server, you use the **:remote console** command to route your queries to that server.
  
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
