# Knowledge Graphs

- Creating structured representations of knowledge with entities, attributes, and relationships.
- Semantic search, question-answering systems, and data integration.

Here's an example of a simple knowledge graph using Gremlin, with some more data to illustrate how it can be set up and queried.

## Entities and Relationships
* People: Alice, Bob, and Carol
* Places: New York, Paris, Tokyo
* Events: Conference2024, Concert2023
* Interests: Music, Travel, Technology

## Relationships
* Alice lives in New York.
* Bob lives in Paris.
* Carol lives in Tokyo.
* Alice and Bob are friends.
* Carol and Alice attended Conference2024.
* Bob and Carol are interested in Music.
* Alice is interested in Travel and Technology.
* Concert2023 was held in New York.
* Conference2024 was held in Tokyo.

## Create vertices and edegs
Vertices
```gremlin
alice = g.addV('person').property('name', 'Alice').next()
bob = g.addV('person').property('name', 'Bob').next()
carol = g.addV('person').property('name', 'Carol').next()
newYork = g.addV('place').property('name', 'New York').next()
paris = g.addV('place').property('name', 'Paris').next()
tokyo = g.addV('place').property('name', 'Tokyo').next()
conference2024 = g.addV('event').property('name', 'Conference2024').next()
concert2023 = g.addV('event').property('name', 'Concert2023').next()
music = g.addV('interest').property('name', 'Music').next()
travel = g.addV('interest').property('name', 'Travel').next()
technology = g.addV('interest').property('name', 'Technology').next()

```

Edges
```gremlin
g.addE('lives_in').from(alice).to(newYork).iterate()
g.addE('lives_in').from(bob).to(paris).iterate()
g.addE('lives_in').from(carol).to(tokyo).iterate()
g.addE('friends_with').from(alice).to(bob).iterate()
g.addE('attended').from(alice).to(conference2024).iterate()
g.addE('attended').from(carol).to(conference2024).iterate()
g.addE('interested_in').from(bob).to(music).iterate()
g.addE('interested_in').from(carol).to(music).iterate()
g.addE('interested_in').from(alice).to(travel).iterate()
g.addE('interested_in').from(alice).to(technology).iterate()
g.addE('held_in').from(concert2023).to(newYork).iterate()
g.addE('held_in').from(conference2024).to(tokyo).iterate()
```

## question-answering 
- Find all friends of Alice:
```gremlin
g.V().has('person', 'name', 'Alice').out('friends_with').values('name')
```

- Who attended Conference2024?:
```gremlin
g.V().has('event', 'name', 'Conference2024').in('attended').values('name')
```

- What are the interests of Bob?:
```gremlin
g.V().has('person', 'name', 'Bob').out('interested_in').values('name')
```

- Which events were held in Tokyo?:
```gremlin
g.V().has('place', 'name', 'Tokyo').in('held_in').values('name')
```