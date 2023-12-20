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
```
