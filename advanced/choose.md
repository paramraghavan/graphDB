```gremlin
g.V().hasLabel('AA').has('AA_id', '{{filter_by_AA}}')
.outE().hasLabel('ttd').inV()
.hasLabel('td').order().by('version', desc)
.limit(1)
.outE().inV()
.choose(
  values('{{filterByTDE}}').is(neq('NA')),
  __.or(
    __.hasLabel('tde').has('{{filterByTDE}}', neq('NA'))
  ),
  __.or(
    __.hasLabel('tde').has('{{filterByTDE}}', 'NA'),
    __.hasLabel('interim'),
    __.hasLabel('tde')
  )
)
.repeat(
  outE().inV()
  .or(
    hasLabel('interim'),
    hasLabel('tde'),
    hasLabel('AA')
  ).simplePath()
)
.path().unfold()
```