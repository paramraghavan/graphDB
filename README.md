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

```gremlin
gremlin> 2+3
==>5

gremlin> a = 5
==>5

gremlin> println "The number is ${a}"
The number is 5

gremlin> for (a in 1..5) {print "${a} "};println()
1 2 3 4 5
```
