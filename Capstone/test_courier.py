"""
test_courier.py  (Phase 4 - correctness evidence)
=================================================
Automatic tests. Every algorithm is compared against a trusted reference:

    sorting      vs  Python's built-in sorted()
    knapsack DP  vs  brute force over ALL subsets of parcels
    Dijkstra     vs  Floyd-Warshall (a different all-pairs algorithm)
    Nearest Nbr  vs  brute-force optimal tour (must never be SHORTER than optimal)

Run with:   python test_courier.py        (or:  pytest test_courier.py)
"""

import random
from itertools import combinations

from data_generator import generate_graph, generate_parcels
from knapsack import greedy_knapsack, knapsack_dp
from planner import plan_all_trips, plan_trip
from shortest_path import dijkstra, reconstruct_path
from sorting import SORTING_ALGORITHMS, merge_sort, parcel_sort_key
from tsp import brute_force_tsp, nearest_neighbor_route, route_length, two_opt


# ------------------------------------------------------------------ sorting
def test_sorting_matches_builtin():
    rng = random.Random(1)
    for name, sort_fn in SORTING_ALGORITHMS.items():
        for n in [0, 1, 2, 5, 50, 300]:
            data = [rng.randint(-100, 100) for _ in range(n)]       # includes duplicates
            assert sort_fn(data) == sorted(data), f"{name} failed for n={n}"


def test_sorting_parcels_by_deadline_then_priority():
    parcels = generate_parcels(200, 20, seed=3)
    for name, sort_fn in SORTING_ALGORITHMS.items():
        result = sort_fn(parcels, key=parcel_sort_key)
        keys = [parcel_sort_key(p) for p in result]
        assert keys == sorted(keys), f"{name} did not sort parcels correctly"


def test_merge_sort_is_stable():
    # Pairs (value, original_position). Sorting by value only must keep positions in order.
    data = [(random.Random(i).randint(0, 4), i) for i in range(100)]
    result = merge_sort(data, key=lambda t: t[0])
    for a, b in zip(result, result[1:]):
        if a[0] == b[0]:
            assert a[1] < b[1], "merge sort changed the order of equal elements"


def test_sorting_does_not_modify_input():
    data = [5, 3, 9, 1]
    copy = data[:]
    for sort_fn in SORTING_ALGORITHMS.values():
        sort_fn(data)
    assert data == copy


# ----------------------------------------------------------------- knapsack
def brute_force_knapsack(parcels, capacity):
    """Try every subset (2^n) - only possible for small n."""
    best = 0
    for r in range(len(parcels) + 1):
        for subset in combinations(parcels, r):
            if sum(p.weight for p in subset) <= capacity:
                best = max(best, sum(p.value for p in subset))
    return best


def test_knapsack_matches_brute_force():
    for seed in range(25):
        parcels = generate_parcels(11, 10, seed)
        for capacity in (10, 25, 40):
            result = knapsack_dp(parcels, capacity)
            assert result.best_value == brute_force_knapsack(parcels, capacity)
            assert result.total_weight <= capacity                       # never overloaded
            assert sum(p.value for p in result.selected) == result.best_value


def test_knapsack_never_worse_than_greedy():
    for seed in range(50):
        parcels = generate_parcels(20, 10, seed)
        assert knapsack_dp(parcels, 40).best_value >= greedy_knapsack(parcels, 40).best_value


def test_knapsack_edge_cases():
    assert knapsack_dp([], 40).best_value == 0                           # no parcels
    parcels = generate_parcels(5, 5, 1)
    assert knapsack_dp(parcels, 0).selected == []                        # van of capacity 0


# ----------------------------------------------------------------- dijkstra
def floyd_warshall(graph):
    """Reference all-pairs shortest paths, O(V^3)."""
    n, INF = graph.num_nodes, float("inf")
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0.0
    for u, v, w in graph.edge_list:
        d[u][v] = min(d[u][v], w)
        d[v][u] = min(d[v][u], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    return d


def test_dijkstra_matches_floyd_warshall():
    for seed in range(10):
        g = generate_graph(25, seed)
        assert g.is_connected()
        fw = floyd_warshall(g)
        for s in range(g.num_nodes):
            dist, prev = dijkstra(g, s)
            for t in range(g.num_nodes):
                assert abs(dist[t] - fw[s][t]) < 1e-6
                # the reconstructed path must really have that length
                path = reconstruct_path(prev, s, t)
                length = sum(next(w for v, w in g.adj[path[i]] if v == path[i + 1])
                             for i in range(len(path) - 1))
                assert abs(length - dist[t]) < 1e-6


# ---------------------------------------------------------------------- TSP
def _dist_for(graph, nodes):
    dist = {}
    for s in nodes:
        d, _ = dijkstra(graph, s)
        dist[s] = {t: d[t] for t in nodes}
    return dist


def test_nearest_neighbor_valid_and_not_better_than_optimal():
    ratios = []
    for seed in range(30):
        g = generate_graph(14, seed)
        stops = random.Random(seed).sample(range(1, 14), 7)
        dist = _dist_for(g, [0] + stops)
        route, length = nearest_neighbor_route(dist, 0, stops)
        assert route[0] == 0 and route[-1] == 0                          # starts and ends at depot
        assert sorted(route[1:-1]) == sorted(stops)                      # every stop exactly once
        _, optimal = brute_force_tsp(dist, 0, stops)
        assert length >= optimal - 1e-9                                  # cannot beat the optimum
        ratios.append(length / optimal)
    assert max(ratios) < 2.0                                             # sanity bound on quality


def test_two_opt_never_worse():
    for seed in range(20):
        g = generate_graph(30, seed)
        stops = random.Random(seed).sample(range(1, 30), 15)
        dist = _dist_for(g, [0] + stops)
        route, length = nearest_neighbor_route(dist, 0, stops)
        better, new_len = two_opt(route, dist)
        assert new_len <= length + 1e-9
        assert sorted(better[1:-1]) == sorted(stops) and better[0] == better[-1] == 0


# ----------------------------------------------------------------- pipeline
def test_pipeline_end_to_end():
    g = generate_graph(20, 5)
    parcels = generate_parcels(40, 20, 5)
    trips, undeliverable = plan_all_trips(g, parcels, capacity=35, use_two_opt=True)
    planned = [p.parcel_id for t in trips for p in t.selected]
    assert len(planned) == len(set(planned))                             # no parcel planned twice
    assert set(planned) | {p.parcel_id for p in undeliverable} == {p.parcel_id for p in parcels}
    for t in trips:
        assert t.knapsack.total_weight <= 35
        assert set(t.stops) == {p.destination for p in t.selected}
        assert abs(route_length(t.route, t.dist) - t.route_km) < 1e-6


def test_pipeline_edge_cases():
    g = generate_graph(8, 1)
    # a parcel heavier than the van is reported as undeliverable, not crashed on
    parcels = generate_parcels(6, 8, 1)
    parcels[0].weight = 500
    trips, undeliverable = plan_all_trips(g, parcels, capacity=30)
    assert [p.parcel_id for p in undeliverable] == [parcels[0].parcel_id]
    # no parcels at all -> no trips
    assert plan_all_trips(g, [], 30) == ([], [])
    # a single parcel -> route Depot -> stop -> Depot
    one = plan_trip(g, generate_parcels(1, 8, 2), 30)
    assert len(one.route) == 3


# ------------------------------------------------------------------- runner
if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {name}  {e}")
    print(f"\n{len(tests) - failed} / {len(tests)} tests passed")
    raise SystemExit(1 if failed else 0)
