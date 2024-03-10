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
        hashcode = generate_consistent_long_from_string(id)
        id_map[vertex['id']]=hashcode

    edges = data.get('edges', [])

    return vertices, edges, id_map


import hashlib


def generate_consistent_long_from_string(input_string):
    # Use SHA-256 hash function
    hasher = hashlib.sha256()
    hasher.update(input_string.encode('utf-8'))
    hashed_bytes = hasher.digest()

    # Convert bytes to a long integer
    long_value = int.from_bytes(hashed_bytes, byteorder='big')
    # Optionally, you can truncate to fit into a specific number of bits
    long_value = long_value & ((1 << 63) - 1)  # Truncate to 63 bits

    return long_value
def hashValue(value:str) -> str:
    hash_obj = hashlib.sha256(value.encode('UTF-8'))
    hex_hash = hash_obj.hexdigest()
    # print(hex_hash)
    return hex_hash