"""Nearest-neighbor TSP approximation using shortest-path distances."""
from .dijkstra import dijkstra

def nearest_neighbor_tsp(graph, start):
    """Build a closed tour visiting all graph nodes; returns (route, distance).

    Distances between stops are shortest-path distances in the supplied graph.
    """
    if start not in graph:
        raise KeyError(f"Unknown start node: {start}")
    unvisited = set(graph) - {start}
    route, total, current = [start], 0, start
    all_distances = {node: dijkstra(graph, node)[0] for node in graph}
    while unvisited:
        nxt = min(unvisited, key=lambda node: (all_distances[current][node], node))
        leg = all_distances[current][nxt]
        if leg == float("inf"):
            raise ValueError(f"No route from {current} to {nxt}")
        total += leg
        route.append(nxt)
        current = nxt
        unvisited.remove(nxt)
    if len(route) > 1:
        back = all_distances[current][start]
        if back == float("inf"):
            raise ValueError(f"No route from {current} back to {start}")
        total += back
        route.append(start)
    return route, total
