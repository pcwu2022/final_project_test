import networkx as nx

DEBUG = True

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

# Debug Print
def debug(*message):
    global DEBUG
    if DEBUG:
        print(*message)

# Read File and Create Graph
def get_graph_from_file(filename) -> SGraph:

    with open(filename, "r") as file:
        input_edges = []
        for line in file.read().splitlines():
            edges = line.split(' ')
            # Exclude self-edges
            if edges[0] != edges[1]:
                input_edges.append((edges[0], edges[1]))

    return SGraph(input_edges)

def remove_successors(s_i):
    successor_list = []
    for u in s_i:
        for v in G.successors(u):
            successor_list.append((u, v))
    for (u, v) in successor_list:
        G.remove_edge(u, v)
    return successor_list

def implication(G: SGraph, i = 1):
    # If the reachable set is the whole set of nodes, return successful
    if len(G.reachable) == len(G.nodes):
        debug(f"Implication Successful at level {i}")
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

        debug(f"Implication: {G.sets[min(i-1, len(G.sets)-1)]} -> {s_i}")
        
        # Remove Edges
        successor_list = remove_successors(s_i)

        # Recursively Call implication
        implication_success = implication(G, i + 1)
        
        # Handle Recursion Result
        if implication_success:
            return True
        
        # Backtrack if Unsuccessful
        G.sets.pop()
        G.reachable = G.reachable.difference(s_i)
        # Restore Removed Edges
        for _ in range(len(successor_list)):
            (u, v) = G.restore_edge()
        return False
    else:
        debug(f"No Further implications found at level {i}")
        return False
    
def run_combination(G: SGraph, k: int):
    s_0 = G.sets[0]
    k0 = len(s_0)
    if k - k0 == 0:
        debug(f"Testing Implication with S0: {s_0}")
        return implication(G, 1)
    s_0_prime = set(G.nodes).difference(s_0)
    for node in s_0_prime:
        # Expand s_0
        G.sets[0].add(node)
        G.reachable.add(node)

        # Remove Successors
        successor_list = remove_successors(set([node]))

        # Recursive Call
        run_success = run_combination(G, k - 1)

        # Handle Recursion Result
        if run_success:
            return True
        
        # Backtrack if Unsuccessful
        G.sets[0].remove(node)
        G.reachable.remove(node)
        for _ in range(len(successor_list)):
            (u, v) = G.restore_edge()
    return False

# Main Algorithm
def kuos_algorithm(G: SGraph):
    # Find s_0
    s_0 = set()
    for node, degree in G.in_degree():
        if degree == 0:
            if node not in G.reachable:
                s_0.add(node)
    k0 = len(s_0)
    G.sets = [s_0]
    G.reachable = G.reachable.union(s_0)
    remove_successors(s_0)
    for k in range(k0, len(G.nodes)):
        success_at_k = run_combination(G, k)
        if success_at_k:
            return G.sets[0]


# Run Algorithm
if __name__ == "__main__":
    G = get_graph_from_file("./data/word_adj_map_3000.txt")
    print(f"Smallest Set: {kuos_algorithm(G)}")