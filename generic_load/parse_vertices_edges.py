import yaml


def load_graph_from_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    vertices = data.get('vertices', [])
    edges = data.get('edges', [])

    return vertices, edges

