# Render
Visualize graph by connecting to AWS Neptune and work working jupyter notebook

>Pre-requisite
>> You should have loaded the airport and routes into the graph  by executing ../example/create_airport_routes_graph.py   

## Setup conda
```shell
$ wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O ~/miniconda.sh
$ ~/miniconda.sh -b -p $HOME/miniconda 
```

## Create and start conda env  
- [Steps to setup Conda Env](https://github.com/paramraghavan/beginners-py-learn/blob/4019888505a849be9bbfda5f4c952b9101277c5a/setup_conda_env.md)

```shell
# -n flag to specify the name of the environment, creates the file
# conda create -n neptune_graph_viz
# This command creates an environment based on the dependencies listed in the "environment.yml" - neptune_graph_viz.yaml file.
conda env create -f ./neptune_graph_viz.yaml
conda activate neptune_graph_viz
# run the following when you update the yaml file
# conda env update -f ./neptune_graph_viz.yaml

# To deactivate an active environment, use
#
#     $ conda deactivate
# list conda envs
conda info --envs
# remove env
conda env remove --name neptune_graph_viz
```

## Create Jupyter Kernel
Once ipykernel is installed, you can create a Jupyter kernel for your Conda environment using the following command:
```shell
# python -m ipykernel install --user --name your_environment_name --display-name "Your Environment Name"
python -m ipykernel install --user --name neptune_graph_viz --display-name "Neptune Graph Viz"

```

# connect to local server
```graph_notebook
#for default tinkerpop server
%%graph_notebook_config
{
  "host": "localhost",
  "port": 8182,
  "ssl": false,
  "gremlin": {
    "traversal_source": "g",
    "username": "",
    "password": "",
    "message_serializer": "graphsonv3"
  }
}

## for neptune
%%graph_notebook_config
{
"host": "neptunedbinstance-xyz.neptune.amazonaws.com",
"neptune_service": "neptune-db",
"load_from_s3_arn": ""
"ssl": true,
"ssl_verify": true,
"aws _region": *us-east-1"
}

# execute gremlin
%%gremlin 
g.V().count()

%%gremlin 
g.V().out().limit(5).path()

%%gremlin 
g.V().outE().inV().path().limit(5)

%%gremlin 
g.V().repeat(out()).times(5).path()

%%gremlin 
g.V().outE().inV().path()

```

## Reference for graph notebook
- https://github.com/aws/graph-notebook?tab=readme-ov-file
- https://github.com/aws/graph-notebook?tab=readme-ov-file#installation


## The generated graph with Lables for Vertices and edges
![Unknown](https://github.com/paramraghavan/tinkerpop/assets/52529498/8372ae04-454e-4aca-bd1d-176f191bd996)


￼

