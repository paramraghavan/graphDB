Implementing automatic metadata capture in a system similar to UDDI (Universal Description, Discovery, and Integration)
involves creating a registry that can dynamically discover and store metadata about various services or components.

Here is a 10000ft design outline:

1. Service Registration:
   Service Provider: Each service provider must have a mechanism to register its service with the metadata registry.
   This can be done through a RESTful API where the provider can submit service details (e.g.,
   service name, description, endpoint URL, and metadata).

   Metadata Extraction: When a service is registered, the system should automatically extract relevant metadata from the
   REST services. This metadata can include operation names, input/output parameters, and data types.

2. Metadata Storage:
   Database Schema: Design a database schema to store the extracted metadata. 

3. Service Discovery:
   Search API: Provide an API or UI for users to search for services based on various criteria (e.g., service name,
   operation name, input/output parameters).

   Query Processing: Implement query processing logic to match user queries against the stored metadata and return
   relevant results.

   4. Metadata Updates:
   Change Detection: Implement a mechanism to detect changes in registered services (e.g., through polling or webhooks).
   Metadata Refresh: And when changes are detected, update the stored metadata to reflect the latest service definition.
