import networkx as nx

# Class for working with Heap & Graph
class SGraph(nx.DiGraph):
    def __init__(self, iterable, **attr):
        super().__init__(iterable, **attr)
        
        # Attributes
        self._edge_restore_stack: list = []

    # Remove an Edge, Save it in a Stack, and Maintain the Heap Structure
    def remove_edge(self, u, v):
        removed_edge = super().remove_edge(u, v)
        self._edge_restore_stack.append((u, v))
        return removed_edge
    
    # Add an Edge and Maintain the Heap Structure
    def add_edge(self, u, v):
        added_edge = super().add_edge(u, v)
        return added_edge

    # Restore the last Edge from the Stack
    def restore_edge(self):
        u, v = self._edge_restore_stack.pop()
        return self.add_edge(u, v)

# Read File and Create Graph
def get_graph_from_file(filename) -> SGraph:

    with open(filename, "r") as file:
        input_edges = [(line.split(' ')[0], line.split(' ')[1]) for line in file.read().splitlines()]

    return SGraph(input_edges)

# Main Algorithm
def kuos_algorithm(G: SGraph):
    pass

# Run Algorithm
if __name__ == "__main__":
    G = get_graph_from_file("./data/sample.in.txt")
    kuos_algorithm(G)

