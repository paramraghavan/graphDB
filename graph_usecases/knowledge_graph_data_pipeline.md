## Entities and Relationships
- Components: SourceA, SourceB, TransformX, TransformY, LoadZ
- Processes: ExtractData, CleanData, AggregateData, LoadData
- Destinations: Database1, DataWarehouse, DataLake

## Relationships
- SourceA and SourceB are used in ExtractData.
- TransformX is applied after ExtractData.
- TransformY is applied after TransformX.
- CleanData and AggregateData use TransformY.
- LoadData is dependent on AggregateData.
- LoadZ is a part of LoadData.
- LoadData sends data to Database1, DataWarehouse, and DataLake.

## Graph Creation
- Adding Vertices  and vertices
```gremlin
// Add Component vertices
g.addV('component').property('name', 'SourceA').as('sourceA')
g.addV('component').property('name', 'SourceB').as('sourceB')
g.addV('component').property('name', 'TransformX').as('transformX')
g.addV('component').property('name', 'TransformY').as('transformY')
g.addV('component').property('name', 'LoadZ').as('loadZ')

// Add Process vertices
g.addV('process').property('name', 'ExtractData').as('extractData')
g.addV('process').property('name', 'CleanData').as('cleanData')
g.addV('process').property('name', 'AggregateData').as('aggregateData')
g.addV('process').property('name', 'LoadData').as('loadData')

// Add Destination vertices
g.addV('destination').property('name', 'Database1').as('database1')
g.addV('destination').property('name', 'DataWarehouse').as('dataWarehouse')
g.addV('destination').property('name', 'DataLake').as('dataLake')

// Add edges
g.addE('used_in').from('sourceA').to('extractData')
g.addE('used_in').from('sourceB').to('extractData')
g.addE('applies').from('transformX').to('extractData')
g.addE('follows').from('transformY').to('transformX')
g.addE('uses').from('cleanData').to('transformY')
g.addE('uses').from('aggregateData').to('transformY')
g.addE('dependent_on').from('loadData').to('aggregateData')
g.addE('part_of').from('loadZ').to('loadData')
g.addE('sends_to').from('loadData').to('database1')
g.addE('sends_to').from('loadData').to('dataWarehouse')
g.addE('sends_to').from('loadData').to('dataLake')

```

## Query
- Find all components used in the ExtractData process:
```gremlin
g.V().has('process', 'name', 'ExtractData').in('used_in').values('name')
```

- List all processes that use TransformY:
```grenlin
g.V().has('component', 'name', 'TransformY').in('uses').values('name')
```

- Find what LoadData sends data to:
```gremlin
g.V().has('process', 'name', 'LoadData').out('sends_to').values('name')
```

- Trace the sequence of processes starting from SourceA:
```gremlin
g.V().has('component', 'name', 'SourceA').outE().inV().repeat(outE().inV()).until(hasLabel('destination')).path().by('name')

```