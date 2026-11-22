"""
shortest_path.py  (Phase 3 - Dijkstra's Algorithm)
==================================================
Dijkstra finds the shortest distance from ONE source node to EVERY other node
in a graph whose edge weights are non-negative.

IDEA (greedy):
  1. dist[source] = 0 and every other node starts at infinity.
  2. Repeatedly pick the unvisited node u with the SMALLEST known distance.
  3. "Relax" every edge (u, v, w): if dist[u] + w < dist[v], we found a shorter
     way to v, so update dist[v] and remember that we came from u (prev[v] = u).

We use a MIN-HEAP (Python's heapq) to pick the smallest node quickly.
Time complexity: O((V + E) log V).
"""

import heapq


def dijkstra(graph, source):
    """
    Returns (dist, prev):
        dist[v] = length of the shortest path source -> v   (inf if unreachable)
        prev[v] = the node just before v on that shortest path (None for the source)
    """
    INF = float("inf")
    dist = [INF] * graph.num_nodes
    prev = [None] * graph.num_nodes
    dist[source] = 0.0

    heap = [(0.0, source)]                    # entries are (distance, node)
    while heap:
        d, u = heapq.heappop(heap)            # node with the smallest distance
        if d > dist[u]:
            continue                          # stale entry (a shorter path was found already)
        for v, w in graph.adj[u]:             # relax all roads leaving u
            new_dist = d + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(heap, (new_dist, v))
    return dist, prev


def reconstruct_path(prev, source, target):
    """
    Follow the prev[] pointers backwards from target to source and reverse them.
    Returns the list of nodes [source, ..., target], or [] if target is unreachable.
    """
    path = []
    current = target
    while current is not None:
        path.append(current)
        current = prev[current]
    path.reverse()
    if not path or path[0] != source:
        return []
    return path
