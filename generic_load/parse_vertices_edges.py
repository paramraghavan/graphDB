import yaml
import sys


def load_graph_from_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    vertices = data.get('vertices', [])

    id_map = {}
    for vertex in vertices:
        id = []
        id.append(vertex['label'])
        for prop, value in vertex['properties'].items():
            id.append(str(value))
        id = ''.join(id)
        hashcode = hash(id) + sys.maxsize + 1
        id_map[vertex['id']]=hashcode

    edges = data.get('edges', [])

    return vertices, edges, id_map

