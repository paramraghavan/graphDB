"""
pipenv install gremlinpython pandas
pipenv install aiohttp async_timeout
Grenlin server needs to be started, apache-tinkerpop-gremlin-server-3.7.1/bin/gremlin-server.sh start
"""

import csv

def read_csv(file_name):
    with open(file_name, mode='r') as file:
        reader = csv.DictReader(file)
        return list(reader)


import pandas as pd

# Read CSV files
accounts_df = pd.read_csv('accounts.csv')
transactions_df = pd.read_csv('transactions.csv')
transfers_df = pd.read_csv('transfers.csv')

# Display the dataframes
print(accounts_df)
print(transactions_df)
print(transfers_df)

# create graph
from gremlin_python import statics
from gremlin_python.structure.io import graphsonV3d0
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal

# Connect to your TinkerPop-enabled graph (update the URI as needed)
g = traversal().withRemote(DriverRemoteConnection('ws://localhost:8182/gremlin','g'))

#
# Creating an in-memory TinkerGraph instance and start
# from gremlin_python.structure.graph import Graph
# import gremlin_python.process.anonymous_traversal
# # Create a new graph instance (TinkerGraph)
# graph = Graph()
# g = graph.traversal()
# # g = gremlin_python.process.anonymous_traversal.traversal()


# Add vertices for accounts
for idx, row in accounts_df.iterrows():
    g.addV('account').property('accountId', row['accountId']).property('holderName', row['holderName']).property('balance', row['balance']).next()

# Add vertices for transactions
for idx, row in transactions_df.iterrows():
    g.addV('transaction').property('transactionId', row['transactionId']).property('amount', row['amount']).next()

# Add edges for transfers
for idx, row in transfers_df.iterrows():
    # A1 to T1
    g.V().has('account', 'accountId', row['fromAccountId']).addE('transfers').to(__.V().has('transaction', 'transactionId', row['transactionId'])).property('date', row['date']).next()
    # T1 to A2
    g.V().has('transaction', 'transactionId', row['transactionId']).addE('transfers').to(__.V().has('account', 'accountId', row['toAccountId'])).property('date', row['date']).next()

# Verify the graph
print(g.V().toList())
print(g.V().valueMap())
print(g.E().toList())
print(g.E().hasLabel('transfers').valueMap())




