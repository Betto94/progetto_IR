from bs4 import BeautifulSoup
# from pprint import pprint
# import json
import networkx as nx
import matplotlib.pyplot as plt

def get_tree_item(tree_section):
    return tree_section.find(class_='CategoryTreeItem')

def get_name(tree_item):
    name = tree_item.find('a').text
    return " ".join(name.replace('\n', '').split())

def get_tree_children(tree_section):
    tree_children = []
    for c in tree_section.find(class_='CategoryTreeChildren'):
        if str(type(c)) != "<class 'bs4.element.NavigableString'>":
            tree_children.append(c)
    return tree_children

class Node:
    serial = 0
    labels = {}
    def __init__(self, name) -> None:
        self.id = Node.serial
        Node.labels[self.id] = name
        Node.serial += 1
        self.name = name
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    def from_tree_item(tree_item):
        return Node(get_name(tree_item))
    
    def __str__(self):
        return f'{self.name}: {len(self.children)} children'
    
    def to_dict(self) -> dict:
        return {
            'label': self.name,
            'children': [c.to_dict() for c in self.children]
        }
    
    def to_graph(self, g=None) -> nx.graph.Graph:
        if g == None:
            g = nx.Graph()

        g.add_node(self.id)
        for c in self.children:
            c.to_graph(g)
            g.add_edge(self.id, c.id)

        return g
        
    
def build_tree(tree_section):
    tree_item = get_tree_item(tree_section)
    children = get_tree_children(tree_section)

    node = Node.from_tree_item(tree_item)
    for c in children:
        node.add_child(build_tree(c))

    return node

if __name__ == '__main__':
    html_doc = ""
    with open('./tree.html', 'r') as f:
        for l in f.readlines():
            html_doc += l

    soup = BeautifulSoup(html_doc, 'html.parser')

    root_div = soup.find(id='root_node')
    tree = build_tree(root_div)
    # pprint(tree.to_dict())

    # with open('category_tree.json', 'w') as f:
    #     json.dump(tree.to_dict(), f)

    # g = tree.children[4].to_graph()
    g = tree.to_graph()
    nx.draw(g, with_labels = True)
    plt.show()
    
