import networkx as nx
from heapdict import heapdict

# Read File and Create Graph
def get_graph_from_file(filename) -> nx.DiGraph:

    with open(filename, "r") as file:
        input_edges = [(line.split(' ')[0], line.split(' ')[1]) for line in file.read().splitlines()]

    return nx.DiGraph(input_edges)

# Main Algorithm
def kuos_algorithm(G: nx.DiGraph):
    pass

# Run Algorithm
if __name__ == "__main__":
    G = get_graph_from_file("./data/sample.in.txt")
    kuos_algorithm(G)

