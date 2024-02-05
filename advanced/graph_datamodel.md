# Graph Data Model
As important as it is to become good at writing effective Gremlin queries, it is equally important, if not more so, to put
careful consideration into how you model your data as a graph. Ideally you want to arrange your graph so that it can 
efficiently support the most common queries that you foresee it needing to handle.

Consider this query description. "Find all flight routes that exist between airports anywhere in the continent of 
Africa and the United States". When putting the air-routes graph together I decided to model continents as their own 
vertices. So each of the seven continents has a vertex. Each vertex is connected to airports within that continent
by an edge labeled "contains".

_I could have chosen to just make the continent a property of each airport vertex but had I done that, to answer the 
question about "routes starting in Africa" I would have to look at every single airport vertex in the graph just to
figure out which continent contained it. By giving each continent its own vertex I am able to greatly simplify
the query we need to write._

Take a look at the query below. We first look just for vertices that are continents. We then only look at the Africa
vertex and the connections it has (each will be to a different airport). By starting the query in this way, we have very
efficiently avoided looking at a large number of the airports in the graph altogether. Finally we look at any routes
from airports in Africa that end up in the United States. This turns out to yield a nice and simple query in no small
part because our data model in the graph made it so easy to do.

```gremlin
  // Flights from any Airport in Africa to any airport in the United States
  g.V().hasLabel('continent').has('code','AF').out().as('a').
        out().has('country','US').as('b').select('a','b').by('code')
```

We could also have started **our query by looking at each airport and looking to see if it is in Africa but that would
involve looking at a lot more vertices.** The point to be made here is that even if our data model is good we still need
to always be thinking about the most efficient way to write our queries.
```gremlin
  // Gives same results but not as efficient
  g.V().hasLabel('airport').as('a').in('contains').has('code','AF').
       .select('a').out().has('country','US').as('b').select('a','b').by('code')
```

## Keeping information in two places within the same graph

Sometimes, to improve query efficiency I find it is actually worth having the data available more than one place within
the same graph. An example of this in the air routes graph would be the way I decided to model countries. I have a
unique vertex for each country but I also store the country code as a property of each airport vertex. In a small graph
this perhaps is overkill but I did it to make a point. Look at the following two queries that return the same results -
the cities in Portugal that have airports in the graph.

```gremlin
g.V().has('country','code','PT').out("contains").values('city')
g.V().has('airport','country','PT').values('city')
```

The first query finds the country vertex for Portugal and then, finds all of the countries connected to it. The second
query looks at all airport vertices and looks to see if they contain PT as the country property.

In the first example it is likely that a lot fewer vertices will get looked at than the first even though a few edges
will also get walked as there are over 3,000 airport vertices but fewer than 300 country vertices. Also, in a production
system with an index in place finding the Portugal vertex should be very fast.

Conversely, if we were already looking at an airport vertex for some other reason and just wanted to see what country it
is in, it is more convenient to just look at the country property of that vertex.

So there is no golden rule here but it is something to think about while designing your data model.

## Using a graph as an index into other data sources

While on the topic of what to keep in the graph, something to resist being drawn into in many cases is the desire to
keep absolutely everything in the graph. For example, in the air routes graph I do not keep every single detail about an
airport (radio frequencies, runway names, weather information etc.) in the airport vertices. That information is
available in other places and easy to find. In a production system you should consider carefully what needs to be in
your graph and what more naturally belongs elsewhere. **One thing I could do is add a URL as a property of each airport
vertex that points to the airports home page or some other resource that has all of the information. In this way the
graph becomes a high quality index into other data sources.** This is a common and useful pattern when working with
graphs. This model of having multiple data sources working together is sometimes referred to as Polyglot storage.

## Supernodes

When a vertex in a graph has a large number of edges and is disproportionately connected to many of the other vertices
in the graph it is likely that many, if not all, graph traversals of any consequence will include that vertex. Such
vertices (nodes) are often referred to as supernodes. In some cases the presence of supernodes may be unavoidable but
with careful planning as you designyour graph model you can reduce the likelihood that vertices become supernodes. The
reason we worry about supernodes is that they can significantly impact the performance of graph traversals. This is
because it is likely that any graph traversal that goes via such a vertex will have to look at most if not all of the
edges connected to that vertex as part of a traversal.

The air-routes graph does not really have anything that could be classed as a supernode. The vertex with the most edges
is the continent vertex for North America that has approximately 980 edges. The busiest airports are IST and AMS and
they both have just over 530 total edges. So in the case of the air-routes graph we do not have to worry too much.

If we were building a graph of a social network that included famous people we might have to worry. Consider some of the
people on Twitter with millions of followers. Without taking some precautions, such a social network, modelled as a
graph, could face issues.

As you design your graph model it is worth considering that some things are perhaps better modelled as a vertex property
than as a vertex with lots of edges needing to connect to it. For example in the air routes graph there are country
vertices and each airport is connected to one of the country vertices. In the air routes graph this is not a problem as
even if all of the airports in the graph were in the same country that would still give us fewer than 3,500 edges
connected to that vertex. **However, imagine if we were building a graph of containing a very large number of people. If
we had several million people in the graph all living in same the country that would be a guaranteed way to get a
supernode if we modelled that relationship by connecting every person vertex to a country vertex using a lives in edge.
In such situations, it would be far more sensible to make the country where a person lives a property of their own
vertex.**

## Path Step Usage and Performance

Using path steps specifically (e.g., path()) can impact performance because they require the traversal engine to keep
track of the paths being traversed. This can increase the memory usage and computation time, especially for long paths
or when many paths are being evaluated.

>> Referenced from https://kelvinlawrence.net/book/PracticalGremlin.pdf
> https://docs.aws.amazon.com/neptune/latest/userguide/feature-overview-data-model.html
