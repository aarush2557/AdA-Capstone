"""
graph.py  (Phase 3 - Customer / Road Graph)
===========================================
GRAPH FORMAT (decided in Phase 1)
---------------------------------
* The road network is an UNDIRECTED, WEIGHTED graph.
* Node 0 is the DEPOT (warehouse). Nodes 1..V-1 are delivery points (customers).
* An edge (u, v, w) is a road between u and v that is w kilometres long.
* Stored as an ADJACENCY LIST:   adj[u] = [(v1, w1), (v2, w2), ...]
  This needs O(V + E) memory - much better than a V x V matrix because a road
  network is SPARSE (each place connects to only a few neighbours).
"""

from collections import deque


class Graph:
    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.adj = [[] for _ in range(num_nodes)]   # adjacency list
        self.coords = []                            # (x, y) of each node (used only for drawing)
        self.edge_list = []                         # every road once: (u, v, w)
        self._edge_set = set()                      # quick "does this road exist?" check

    # ------------------------------------------------------------------
    def add_edge(self, u, v, w):
        """Add a two-way road of length w between nodes u and v."""
        if w < 0:
            raise ValueError("Dijkstra needs non-negative edge weights")
        self.adj[u].append((v, w))
        self.adj[v].append((u, w))
        self.edge_list.append((u, v, w))
        self._edge_set.add((min(u, v), max(u, v)))

    def has_edge(self, u, v):
        return (min(u, v), max(u, v)) in self._edge_set

    @property
    def num_edges(self):
        return len(self.edge_list)

    # ------------------------------------------------------------------
    def is_connected(self):
        """Breadth-first search from the depot: True if every node can be reached."""
        seen = {0}
        queue = deque([0])
        while queue:
            u = queue.popleft()
            for v, _ in self.adj[u]:
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        return len(seen) == self.num_nodes

    def name(self, u):
        """Human-readable node name: 'Depot' for node 0, otherwise 'C<number>'."""
        return "Depot" if u == 0 else f"C{u}"

    # ------------------------------------------------------------------
    # Save / load as plain dictionaries so datasets can be stored in JSON files.
    def to_dict(self):
        return {
            "num_nodes": self.num_nodes,
            "coords": [list(c) for c in self.coords],
            "edges": [list(e) for e in self.edge_list],
        }

    @classmethod
    def from_dict(cls, data):
        g = cls(data["num_nodes"])
        g.coords = [tuple(c) for c in data["coords"]]
        for u, v, w in data["edges"]:
            g.add_edge(u, v, w)
        return g

    def adjacency_text(self):
        """Printable adjacency list, one line per node."""
        lines = []
        for u in range(self.num_nodes):
            neighbours = ", ".join(f"{self.name(v)}({w})" for v, w in self.adj[u])
            lines.append(f"  {self.name(u):<6} -> {neighbours}")
        return "\n".join(lines)
