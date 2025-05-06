import networkx as nx

# Class for working with Heap & Graph
class SGraph(nx.DiGraph):
    def __init__(self, iterable, **attr):
        super().__init__(iterable, **attr)
        
        # Public Attributes
        self.sets: list = []
        self.reachable: set = set()

        # Intermal Attributes
        self._edge_restore_stack: list = []

    # Remove an Edge and Save it in a Stack
    def remove_edge(self, u, v):
        removed_edge = super().remove_edge(u, v)
        self._edge_restore_stack.append((u, v))
        return removed_edge

    # Restore the last Edge from the Stack
    def restore_edge(self):
        u, v = self._edge_restore_stack.pop()
        self.add_edge(u, v)
        return (u, v)

# Read File and Create Graph
def get_graph_from_file(filename) -> SGraph:

    with open(filename, "r") as file:
        input_edges = [(line.split(' ')[0], line.split(' ')[1]) for line in file.read().splitlines()]

    return SGraph(input_edges)

def implication(G: SGraph, i = 0):
    # If the reachable set is the whole set of nodes, return successful
    if len(G.reachable) == len(G.nodes):
        return True
    
    # Find all nodes with in_degree 0
    s_i = set()
    for node, degree in G.in_degree():
        if degree == 0:
            if node not in G.reachable:
                s_i.add(node)
    if len(s_i) != 0:
        # Update New Reachable Set
        G.sets.append(s_i)
        G.reachable = G.reachable.union(s_i)
        
        # Remove Edges
        successor_list = []
        for u in s_i:
            for v in G.successors(u):
                successor_list.append((u, v))
        for (u, v) in successor_list:
            G.remove_edge(u, v)
            print(f"Removed edge ({u}, {v}) at level {i}")

        # Recursively Call implication
        implication_success = implication(G, i + 1)
        
        # Handle Recursion Result
        if not implication_success:
            # Backtrack if Unsuccessful
            G.sets.pop()
            G.reachable = G.reachable.difference(s_i)
            # Restore Removed Edges
            for _ in range(len(successor_list)):
                (u, v) = G.restore_edge()
                print(f"Restored edge ({u}, {v}) at level {i}")
            return False
        return True
    else:
        print(f"Implication Failed at level {i}")
        return False
    

# Main Algorithm
def kuos_algorithm(G: SGraph, k = 0):
    implication(G, 0)


# Run Algorithm
if __name__ == "__main__":
    G = get_graph_from_file("./data/sample.in.txt")
    kuos_algorithm(G)

