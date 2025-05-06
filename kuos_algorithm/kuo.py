import networkx as nx

# Read File
input_filename = "./data/sample.in.txt"

with open(input_filename, "r") as file:
    input_edges = [(line.split(' ')[0], line.split(' ')[1]) for line in file.read().splitlines()]

# Create Graph
G = nx.DiGraph(input_edges)

print(G._node)

