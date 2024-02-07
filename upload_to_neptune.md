# How to load vertex and edge's into AWs Neptune
Here the example uses airport as vertex and routes as edge

## Step 1: Preparing the CSV Files
- You'll need two CSV files: one for the vertices (airports) and one for the edges (routes).
- Vertex -airports.csv. The first row should define the property keys, starting with ~id and ~label. ~id is a unique
  identifier for each vertex, and ~label is the vertex label. **code and name** are the property of the vertex
```csv
~id,~label,code:String,name:String
JFK,airport,JFK,John F. Kennedy International Airport
LAX,airport,LAX,Los Angeles International Airport
```
- Edge - routes.csv. The first row should include ~id, ~from, ~to, and ~label. ~from and ~to refer to the ~id of the
  source and target vertices, respectively. **distance** is the property of this edge.
```csv
~id,~from,~to,~label,distance:Int
route1,JFK,LAX,route,2475
route2,LAX,JFK,route,2475
```

## Step 2: Uploading the CSV Files to Amazon S3
```shell
aws s3 cp airports.csv s3://your-bucket-name/
aws s3 cp routes.csv s3://your-bucket-name/
```

Step 3: Loading Data into Neptune Using curl
- Load Vertices:
```shell
curl -X POST \
    -H 'Content-Type: application/json' \
    http://your-neptune-endpoint:8182/loader -d '
    {
      "source" : "s3://your-bucket-name/airports.csv",
      "format" : "csv",
      "iamRoleArn" : "your-iam-role-arn",
      "region" : "your-region",
      "failOnError" : "FALSE"
    }
curl -X POST \
    -H 'Content-Type: application/json' \
    https://your-neptune-endpoint:8182/loader -d '
{
  "source" : "s3://your-bucket-name/",
  "format" : "csv",
  "iamRoleArn" : "your-iam-role",
  "region" : "your-region",
  "failOnError" : "FALSE",
  "parallelism" : "MEDIUM",
  "updateSingleCardinalityProperties" : "FALSE",
  "files" : [ "airports.csv", "routes.csv" ]
}'    
```
- Load Edges
```shell
curl -X POST \
    -H 'Content-Type: application/json' \
    http://your-neptune-endpoint:8182/loader -d '
    {
      "source" : "s3://your-bucket-name/routes.csv",
      "format" : "csv",
      "iamRoleArn" : "your-iam-role-arn",
      "region" : "your-region",
      "failOnError" : "FALSE"
    }'
```
- Load Vertices and Edges together
```shell
curl -X POST \
    -H 'Content-Type: application/json' \
    https://your-neptune-endpoint:8182/loader -d '
{
  "source" : "s3://your-bucket-name/",
  "format" : "csv",
  "iamRoleArn" : "your-iam-role",
  "region" : "your-region",
  "failOnError" : "FALSE",
  "parallelism" : "MEDIUM",
  "updateSingleCardinalityProperties" : "FALSE",
  "files" : [ "airports.csv", "routes.csv" ]
}'

curl -X POST https://your-neptune-endpoint:port/loader \
     -H 'Content-Type: application/json' \
     -d '
     {
       "source" : "s3://bucket-name/object-key-name",
       "format" : "opencypher",
       "userProvidedEdgeIds": "TRUE",
       "iamRoleArn" : "arn:aws:iam::account-id:role/role-name",
       "region" : "region",
       "failOnError" : "FALSE",
       "parallelism" : "MEDIUM",
     }'

```
```python
import requests

headers = {
    'Content-Type': 'application/json',
}

data = {
     "source" : "s3://bucket-name/object-key-name",
     "format" : "opencypher",
     "userProvidedEdgeIds": "TRUE",
     "iamRoleArn" : "arn:aws:iam::account-id:role/role-name",
     "region" : "region",
     "failOnError" : "FALSE",
     "parallelism" : "MEDIUM",
}

response = requests.post('http://fiddle.jshell.net/echo/html/', headers=headers, data=data)
```

- ref https://docs.aws.amazon.com/neptune/latest/userguide/load-api-reference-load.html
- Replace your-neptune-endpoint, your-bucket-name, your-iam-role-arn, and your-region with your specific details.
- https://curlconverter.com/python/

## Ensuring No Duplicates
To make sure an airport is not uploaded twice:
- Use unique identifiers in the ~id column for each airport. Neptune will treat each row with a different ~id as a
  separate vertex.
- If you're updating existing data and don't want to create duplicate vertices, set updateSingleCardinalityProperties to
  TRUE in your load job. This will update properties of existing vertices instead of creating new ones.


## Step 4: Loading Data into Neptune Using AWS CLI

- Load Vertices:
```shell
aws neptune start-load --source "s3://your-bucket-name/airports.csv" \
    --format "csv" --iam-role-arn "your-iam-role-arn" \
    --region "your-region" --neptune-endpoint "your-neptune-endpoint"
```
- Load Edges:
```shell
aws neptune start-load --source "s3://your-bucket-name/routes.csv" \
    --format "csv" --iam-role-arn "your-iam-role-arn" \
    --region "your-region" --neptune-endpoint "your-neptune-endpoint"
```

## updateSingleCardinalityProperties" : "FALSE", ?
- updateSingleCardinalityProperties: "FALSE": This setting means that the load job will not update properties of
  existing vertices or edges if a record in the CSV file has the same ID as an existing vertex or edge. Instead, Neptune
  will treat each row in the CSV file as a new vertex or edge. As a result, you might end up with duplicate vertices or
  edges if your CSV files contain IDs that already exist in the database.
### Implications of Setting to "FALSE":
- Duplicate Entries: If the CSV file contains vertices or edges with IDs that already exist in your graph, Neptune will
  create new vertices or edges with the same IDs, leading to duplicates.
- Data Integrity: This setting is important for maintaining data integrity. If you are sure that your CSV file contains
  only new data that doesn't overlap with existing data in the graph, setting this to "FALSE" is appropriate.

## updateSingleCardinalityProperties to "TRUE":
- When set to "TRUE", Neptune updates the properties of existing vertices or edges if their IDs are found in the CSV
  file. This is useful for data updates or corrections without duplicating the vertices or edges.
- **Vertex/Edge Does Not Exist:** The loader will create a new vertex or edge with the properties specified in your CSV
  file. The ID provided in the CSV file will be used for this new vertex or edge.
- **Vertex/Edge Exists:** If a vertex or edge with the same ID already exists in the graph, and the CSV file contains
  updated values for its properties, these properties will be updated in the graph. This update only applies to
  properties with single cardinality.

**Summary**
By setting updateSingleCardinalityProperties to "TRUE", you can manage the updates to your graph data more effectively,
ensuring that new data is inserted where necessary and existing data is updated as needed, without creating unwanted
duplicates.

## Cardinality

In graph databases, the concept of "cardinality" refers to the number of values that a property of a vertex or edge can
hold. When a property is defined as having "single cardinality", it means that this property can only have one value at
any given time for a particular vertex or edge. If you try to add another value to a single cardinality property, it
replaces the existing value.
- Example: Let's consider a graph of airports and routes. Each airport vertex has properties like **code, name, and city**.
- **Single Cardinality Property:** Suppose the code property of an airport vertex is designed to have single
  cardinality. This means each airport vertex can have only one code.
  - If an airport vertex initially has code as 'JFK', and you later update this code to 'JFK1', the new code 'JFK1' will
    replace the old code 'JFK'. After the update, the code property can only reflect 'JFK1'.
- **List or Set Cardinality:** list or set cardinality can hold multiple values.
  - if an airport vertex has a property aliases with list cardinality, it could contain multiple values
    like ['JFK', 'Kennedy', 'NY Airport']. Adding another alias doesn't replace these values but adds to the list.

## Choosing Cardinality
When modeling your data in a graph database, choosing the right cardinality for a property is important. 
- Single cardinality is suitable for properties that are inherently unique to each vertex or edge, like an airport's
  code or a person's social security number.
- List or set cardinality is more appropriate for properties that can naturally have multiple values, like a person's
  list of email addresses or an airport's list of alias names.