import networkx as nx
import heapq
from typing import Set, List, Tuple, Dict
import time

class SGraph(nx.DiGraph):
    """Enhanced directed graph for Kuo's algorithm with efficient backtracking."""
    
    def __init__(self, iterable=None, **attr):
        super().__init__(iterable, **attr)
        # Sets discovered at each level
        self.sets: List[Set] = []
        # All reachable nodes so far
        self.reachable: Set = set()
        # Stack for edge restoration during backtracking
        self._edge_restore_stack: List[Tuple] = []
        # Cache node degrees for faster access
        self._in_degree_cache: Dict = {}
        self._refresh_degree_cache()
    
    def _refresh_degree_cache(self):
        """Update in-degree cache for all nodes."""
        self._in_degree_cache = dict(self.in_degree())
    
    def get_zero_indegree_nodes(self, exclude_reachable=True) -> Set:
        """Get all nodes with in-degree 0, optionally excluding already reachable nodes."""
        zero_degree_nodes = {node for node, degree in self._in_degree_cache.items() if degree == 0}
        if exclude_reachable:
            return zero_degree_nodes - self.reachable
        return zero_degree_nodes
    
    def remove_edge(self, u, v):
        """Remove edge and update degree cache."""
        removed_edge = super().remove_edge(u, v)
        self._edge_restore_stack.append((u, v))
        # Update in-degree for the target node
        self._in_degree_cache[v] -= 1
        return removed_edge
    
    def restore_edge(self):
        """Restore edge from stack and update degree cache."""
        if not self._edge_restore_stack:
            return None
        u, v = self._edge_restore_stack.pop()
        self.add_edge(u, v)
        # Update in-degree for the target node
        self._in_degree_cache[v] += 1
        return (u, v)
    
    def remove_node_successors(self, nodes: Set) -> int:
        """Remove all outgoing edges from a set of nodes. Returns count of removed edges."""
        successor_list = []
        for u in nodes:
            for v in self.successors(u):
                successor_list.append((u, v))
        
        for (u, v) in successor_list:
            self.remove_edge(u, v)
        
        return len(successor_list)


def get_graph_from_file(filename) -> SGraph:
    """Create graph from file with more efficient parsing."""
    with open(filename, "r") as file:
        input_edges = []
        for line in file:
            edges = line.strip().split()
            if len(edges) >= 2 and edges[0] != edges[1]:  # Exclude self-edges
                input_edges.append((edges[0], edges[1]))

    return SGraph(input_edges)


def score_node(graph: SGraph, node) -> float:
    """Score a node based on its connectivity properties for heuristic selection.
    Higher scores indicate better candidates for inclusion in S0.
    """
    # Prioritize nodes with many outgoing edges
    out_degree = graph.out_degree(node)
    
    # But penalize nodes with many incoming edges (those might be reached via implication)
    in_degree = graph.in_degree(node)
    
    # Calculate how many new nodes this would reach directly
    new_successors = set(graph.successors(node)) - graph.reachable
    
    # Base score is out_degree - in_degree to prefer "source-like" nodes
    base_score = out_degree - in_degree
    
    # Boost score based on how many new nodes this would reach
    reach_score = len(new_successors) * 2
    
    return base_score + reach_score


def implication(graph: SGraph, debug_mode=False, level=1) -> bool:
    """Run the implication process to find reachable nodes."""
    # If all nodes are reachable, we're done
    if len(graph.reachable) == len(graph.nodes):
        if debug_mode:
            print(f"Implication successful at level {level}")
        return True
    
    # Find all nodes with in-degree 0 (not already reached)
    s_i = graph.get_zero_indegree_nodes()
    
    if s_i:
        # Update reachable set with newly discovered nodes
        graph.sets.append(s_i)
        graph.reachable.update(s_i)
        
        if debug_mode:
            print(f"Implication level {level}: {s_i}")
        
        # Remove outgoing edges from these nodes
        edge_count = graph.remove_node_successors(s_i)
        
        # Recursively continue implication
        success = implication(graph, debug_mode, level + 1)
        
        # If successful, we're done
        if success:
            return True
        
        # Otherwise backtrack: restore edges and update reachable set
        graph.sets.pop()
        graph.reachable.difference_update(s_i)
        for _ in range(edge_count):
            graph.restore_edge()
            
        return False
    else:
        if debug_mode:
            print(f"No further implications found at level {level}")
        return False


def find_candidates(graph: SGraph, k_remaining: int) -> List:
    """Find the best candidate nodes to include in S0 based on heuristic scoring."""
    # Candidates are nodes not yet in S0 or reachable
    candidates = set(graph.nodes) - graph.reachable
    
    # Score and rank candidates
    scored_candidates = [(score_node(graph, node), node) for node in candidates]
    
    # Return top k_remaining + buffer candidates
    buffer = min(10, len(scored_candidates))  # Include some extra candidates
    return [node for _, node in heapq.nlargest(k_remaining + buffer, scored_candidates)]


def run_combination(graph: SGraph, k: int, debug_mode=False) -> bool:
    """Try to find a valid S0 of size k using backtracking with heuristics."""
    s_0 = graph.sets[0]
    k0 = len(s_0)
    
    # If we already have enough nodes in S0, try implication
    if k0 >= k:
        if debug_mode:
            print(f"Testing implication with S0: {s_0}")
        return implication(graph, debug_mode)
    
    # Find the best candidates to try
    candidates = find_candidates(graph, k - k0)
    
    for node in candidates:
        # Skip if node is already reachable
        if node in graph.reachable:
            continue
            
        # Add node to S0 and reachable set
        graph.sets[0].add(node)
        graph.reachable.add(node)
        
        # Remove outgoing edges
        edge_count = graph.remove_node_successors({node})
        
        # Recurse
        success = run_combination(graph, k, debug_mode)
        
        # If successful, we're done
        if success:
            return True
            
        # Otherwise backtrack
        graph.sets[0].remove(node)
        graph.reachable.remove(node)
        for _ in range(edge_count):
            graph.restore_edge()
            
    return False


def kuos_algorithm(graph: SGraph, debug_mode=False, timeout_seconds=300):
    """Run Kuo's algorithm with timeout and performance enhancements."""
    start_time = time.time()
    
    # Initialize with nodes having zero in-degree
    s_0 = graph.get_zero_indegree_nodes()
    k0 = len(s_0)
    
    graph.sets = [s_0]
    graph.reachable = s_0.copy()
    
    # Remove outgoing edges from initial set
    graph.remove_node_successors(s_0)
    
    if debug_mode:
        print(f"Starting with initial set S0: {s_0} (size {k0})")
    
    # Try increasing sizes of S0
    for k in range(k0, len(graph.nodes) + 1):
        # Check for timeout
        if time.time() - start_time > timeout_seconds:
            if debug_mode:
                print(f"Timeout after {timeout_seconds} seconds")
            return graph.sets[0], False
            
        if debug_mode:
            print(f"Trying to find solution with k={k}")
            
        # Try to find a solution with k nodes
        success = run_combination(graph, k, debug_mode)
        
        if success:
            if debug_mode:
                print(f"Found solution with {k} nodes: {graph.sets[0]}")
            return graph.sets[0], True
    
    # Should never reach here unless graph is empty
    return set(), False


if __name__ == "__main__":
    # Command line argument handling
    import argparse
    parser = argparse.ArgumentParser(description='Run improved Kuo\'s algorithm')
    parser.add_argument('--file', type=str, default="./data/word_adj_map_3000.txt", 
                        help='Input graph file')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--timeout', type=int, default=300, 
                        help='Timeout in seconds (default: 300)')
    args = parser.parse_args()
    
    # Run the algorithm
    print(f"Loading graph from {args.file}")
    G = get_graph_from_file(args.file)
    print(f"Graph loaded with {len(G.nodes)} nodes and {len(G.edges)} edges")
    
    start_time = time.time()
    smallest_set, completed = kuos_algorithm(G, args.debug, args.timeout)
    end_time = time.time()
    
    print(f"Algorithm {'completed' if completed else 'timed out'} in {end_time - start_time:.2f} seconds")
    print(f"Smallest set found: {smallest_set}")
    print(f"Set size: {len(smallest_set)}")