# import os
import networkx as nx
import json
import sys

def dfs_build_tree(json_tree : dict, g: nx.Graph | None = None) -> nx.Graph:

    label = json_tree['label']
    if g == None:
        g = nx.Graph()
        g.add_node(label.lower())

    for c in json_tree['children']:
        g.add_node(c['label'].lower())
        g.add_edge(label.lower(), c['label'].lower())
        dfs_build_tree(c, g)

    return g


def build_tree(file_name:str):
    # path = os.path.join("/home/alessandro/projects/gabriele/progetto_IR/src/main/resources/static", file_name)
    with open(file_name, 'r') as f:
        data = json.load(f)
        g = dfs_build_tree(data)
        return g

if __name__ == '__main__':
    category = sys.argv[1]

    file_name = 'category_tree.json'
    g = build_tree(file_name)
    
    try:
        paths = list(nx.all_shortest_paths(g, 'medicine', category.lower()))
        print(paths)
    except:
        print([])
