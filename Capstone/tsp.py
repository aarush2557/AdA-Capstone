"""
tsp.py  (Phase 3 - Route Planning with TSP approximation)
=========================================================
Visiting all delivery points of a trip and coming back to the depot is the
TRAVELLING SALESMAN PROBLEM (TSP). TSP is NP-hard: the exact answer needs
checking (k-1)! orders for k stops, which is impossible for large k.
So we use an APPROXIMATION algorithm:

    NEAREST NEIGHBOUR  - from the current place always drive to the closest
                         stop that has not been visited yet.
    Time O(k^2).  It is fast but not optimal (on average about 5-25 % longer than the
    best tour on random maps).

Extra (used for the "optimisation" part of Phase 4):
    2-OPT              - improves a tour by reversing parts of it while that
                         shortens the total length.
    BRUTE FORCE        - tries every order; only for tiny inputs, used to PROVE
                         how good the approximation is.

All functions receive `dist`, a dictionary of dictionaries where
dist[a][b] = shortest road distance (from Dijkstra) between place a and place b.
"""

from itertools import permutations


def route_length(route, dist):
    """Total length of a route given as a list of nodes [d, s1, s2, ..., d]."""
    return sum(dist[route[i]][route[i + 1]] for i in range(len(route) - 1))


def nearest_neighbor_route(dist, depot, stops):
    """
    Build a closed tour depot -> stops (in nearest-neighbour order) -> depot.
    Returns (route, length).
    """
    unvisited = set(stops)
    route = [depot]
    current = depot
    while unvisited:
        # Pick the closest unvisited stop. The tuple (distance, id) breaks ties
        # by node number so the result is always the same (deterministic).
        nxt = min(unvisited, key=lambda s: (dist[current][s], s))
        route.append(nxt)
        unvisited.remove(nxt)
        current = nxt
    route.append(depot)                       # drive back to the depot
    return route, route_length(route, dist)


def two_opt(route, dist, max_passes=100):
    """
    2-opt local search. For two positions i < j, reversing the part of the tour
    between them replaces edges (a,b) and (c,d) with (a,c) and (b,d).
    If the new edges are shorter, we keep the change. Repeat until no swap helps.
    The depot at both ends of the route is never moved.
    """
    best = route[:]
    improved = True
    passes = 0
    while improved and passes < max_passes:
        improved = False
        passes += 1
        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best) - 1):
                a, b = best[i - 1], best[i]
                c, d = best[j], best[j + 1]
                # Change in length if we reverse the segment best[i..j]
                delta = dist[a][c] + dist[b][d] - dist[a][b] - dist[c][d]
                if delta < -1e-9:             # strictly shorter -> accept
                    best[i:j + 1] = reversed(best[i:j + 1])
                    improved = True
    return best, route_length(best, dist)


def brute_force_tsp(dist, depot, stops):
    """Exact optimum by trying every order of the stops. Only for <= 9 stops."""
    if len(stops) > 9:
        raise ValueError("brute force is only meant for 9 stops or fewer")
    best_route, best_len = None, float("inf")
    for order in permutations(stops):
        route = [depot, *order, depot]
        length = route_length(route, dist)
        if length < best_len:
            best_route, best_len = route, length
    return best_route, best_len
