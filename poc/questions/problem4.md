How to parse the query result using gremlin python in generic way and create a json for d3.js consumption:
g.V().repeat(bothE().otherV()).times(3).path().by(elementMap())
