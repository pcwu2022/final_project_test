import networkx as nx
import heapq

def get_graph_from_file(filename):
    # Read File

    with open(filename, "r") as file:
        input_edges = [(line.split(' ')[0], line.split(' ')[1]) for line in file.read().splitlines()]

    # Create Graph
    return nx.DiGraph(input_edges)

def kuos_algorithm(G):
    # Create Heap for storing the elements
    heap = []
    for node, degree in G.in_degree():
        heapq.heappush(heap, (degree, node))

# Run Algorithm
if __name__ == "__main__":
    G = get_graph_from_file("./data/sample.in.txt")
    kuos_algorithm(G)

