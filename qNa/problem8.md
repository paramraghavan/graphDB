# How to add a new property to the edge to-result and update it's status to passed or failed based on the node result's property  status - passed or failed

g.V(). hasLabel('ruleset'). repeat( outE('to-rule'). inV(). hasLabel('rule'). coalesce( outE('to-result').inV()
.hasLabel('result') .order().by('created_timestamp', desc) .limit(1), identity() // Stay at current Rule vertex ) ).
emit(). path(). by(elementMap())

