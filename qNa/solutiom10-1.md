

```python
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.graph_traversal import __
import pandas as pd


def get_asset_users(neptune_endpoint, asset_id):
    """
    Query AWS Neptune to find all users associated with a given asset through the specified relationship path.
    
    Parameters:
    neptune_endpoint (str): Neptune cluster endpoint URL
    asset_id (str): ID of the asset to query
    
    Returns:
    pandas.DataFrame: DataFrame containing the complete path from asset to users
    """

    # Create a connection to Neptune
    conn = DriverRemoteConnection(
        f'wss://{neptune_endpoint}:8182/gremlin',
        'g'
    )

    # Create a graph traversal source
    g = traversal().withRemote(conn)

    try:
        # Execute the Gremlin query
        results = (
            g.V().hasLabel('asset').has('id', asset_id)  # Start from the asset
            .as_('asset')  # Label the asset vertex
            .in_('asset_profile')  # Traverse to asset_profile
            .as_('asset_profile')  # Label the asset_profile vertex
            .in_('profile')  # Traverse to profile
            .as_('profile')  # Label the profile vertex
            .in_()  # Traverse to user
            .as_('user')  # Label the user vertex
            .select('asset', 'asset_profile', 'profile', 'user')  # Select all vertices in the path
            .by(__.valueMap(True))  # Get all properties including label
            .toList()
        )

        # Transform results into a more manageable format
        transformed_data = []
        for result in results:
            row = {
                'asset_id': result['asset'].get('id', [None])[0],
                'asset_label': result['asset'].get('label', 'asset'),
                'asset_profile_id': result['asset_profile'].get('id', [None])[0],
                'asset_profile_label': result['asset_profile'].get('label', 'asset_profile'),
                'profile_id': result['profile'].get('id', [None])[0],
                'profile_label': result['profile'].get('label', 'profile'),
                'user_id': result['user'].get('id', [None])[0],
                'user_label': result['user'].get('label', 'user')
            }
            transformed_data.append(row)

        # Create DataFrame
        df = pd.DataFrame(transformed_data)
        return df

    finally:
        # Close the connection
        conn.close()


# Example usage
if __name__ == "__main__":
    # Replace with your Neptune endpoint
    NEPTUNE_ENDPOINT = "your-neptune-cluster.cluster-xxxxxxxxxxxx.region.neptune.amazonaws.com"
    ASSET_ID = "asset123"  # Replace with actual asset ID

    df = get_asset_users(NEPTUNE_ENDPOINT, ASSET_ID)
    print("Users associated with asset:")
    print(df)

```

I've created a Python script that:

1. Implements the Gremlin query to traverse from asset to users following the path:
    - asset <--- asset_profile <--- profile <--- user

2. The query:
    - Starts from the specified asset
    - Labels each vertex in the path for later selection
    - Collects all properties of each vertex using valueMap(True)
    - Returns the complete path information

3. Transforms the results into a pandas DataFrame with columns:
    - asset_id and asset_label
    - asset_profile_id and asset_profile_label
    - profile_id and profile_label
    - user_id and user_label

To use this code:

- Install required packages:

```python
pip
install
gremlinpython
pandas
```