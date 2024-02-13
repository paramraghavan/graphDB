# Designing a graph database

## Know your Data and Queries
Before designing your graph database you have to have a clear understanding of the data you will store and the queries you will run. 
How you define nodes, relationships, properties, and indexes will help you structure/design your graph database.

## Define Nodes(Vertices) and  Relationship(Edges)
Nodes represent entities in your graph database, and relationships represent how those entities are connected. It's
crucial define these elements, based on types of entities you have and how they relate to each other.
Think about which entities should be nodes, the relationships that connect these nodes.

## Identifying Labels for Nodes and Relationships

**Analyze the Domain:**
Start by  analyzing your data domain. Identify the key entities and their attributes.
For nodes, these entities might be objects or concepts like Person, Company, Event, etc. For relationships, identify
how these entities interact, such as EMPLOYED_BY(Person-employedBy--> Company), (Person-attended--> Event)ATTENDED, etc

**Queries:**
 Identify which entities and relationships are involved in these queries. Labels should be chosen to optimize
these queries. Use clear, descriptive names for labels that accurately represent the entity or relationship. 
 It's often helpful to use nouns for entity labels and verb phrases for relationship labels.

_Query Optimization:_ Labels can significantly improve query performance by allowing you to narrow down searches to 
specific types of nodes or relationships. Use labels to filter queries, ensuring that they are as efficient as possible.
For example, you tag the Source node with Labels - S3, Snowflake, rDBMS, etc., you are only interested in S3 nodes,
you can directly query for those nodes without scanning through other unrelated Source type nodes

_Logical Structure/Schema Design:_ Graph databases are schema-less or have flexible schemas, using labels allows 
you to impose a logical structure on your data. 

_Multiple labels to Node and Edges:_
Amazon Neptune does not support assigning multiple labels directly to relationships (edges) within its graph database.
In Neptune, each edge is defined with a single label (or edge type) that specifies the nature. If you need to represent
a multi-labelled relationship, then it is suggested to use multiple edges in this case.

**Composite Labels**  
Create a composite label that combines multiple concepts into one. For example, if you need to label a relationship 
as both "friend" and "colleague," you could create a composite label like "Friend_Colleague." This approach is 
straightforward but can quickly become unwieldy if there are many combinations of labels.

**Using Properties:**
Another approach is to use properties on the relationships to indicate additional types or categories. For instance, you
could have a primary label for the relationship type and then add a property to further specify other aspects of the
relationship.

**Nodes**
it is possible to apply multiple labels to a single node, allowing for a more nuanced classification of entities. This
feature can be particularly useful in complex domains where an entity might fulfill multiple roles or belong to multiple
categories. for example source could be S3, Snowflake,RDBMS,etc..

**Neptune supports multiple labels for a vertex.** When you create a label, you can specify multiple labels by separating
them with ::. For example, g.addV("Label1::Label2::Label3") adds a vertex with three different labels. The hasLabel step
matches this vertex with any of those three labels: hasLabel("Label1"), hasLabel("Label2"), and hasLabel("Label3").

## Indexing
Neptune automatically indexes labels and relationship types, which helps in maintaining fast query 
performance as your graph grows. Make sure to leverage these indexes in your queries by specifying labels and 
types wherever possible.

## Consider Graph Model vs. Query Performance:
The way you model your graph can affect query performance. In some cases, denormalizing your data (e.g., adding
redundant relationships to avoid long traversals) can improve performance for read-heavy applications. Keep in mind that
this can also lead to increased complexity and storage requirements.

>> Reference: https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-differences.html