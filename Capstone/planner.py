"""
planner.py  (the integration layer - ties ALL phases together)
==============================================================
Pipeline for ONE delivery trip:

    parcels ──► [1] Merge Sort (by deadline / priority)
            ──► [2] 0/1 Knapsack DP (which parcels fit in the van?)
            ──► [3] Dijkstra from the depot and from every stop (real road paths)
            ──► [4] Nearest-Neighbour TSP (+ optional 2-opt) (order of the stops)
            ──► ordered route, total km, arrival times

plan_all_trips() repeats this until every deliverable parcel has been planned.
"""

import time
from dataclasses import dataclass, field

from knapsack import knapsack_dp
from shortest_path import dijkstra, reconstruct_path
from sorting import merge_sort, parcel_sort_key
from tsp import nearest_neighbor_route, route_length, two_opt

DEPOT = 0                  # node number of the warehouse
SPEED_KMPH = 40.0          # average van speed used to estimate arrival times
LOADING_HOURS = 0.25       # time to re-load the van between two trips


@dataclass
class TripPlan:
    """All results of one planned trip (kept together so main.py can print them)."""
    trip_no: int
    start_time: float
    sorted_parcels: list                  # parcels after Merge Sort
    knapsack: object                      # KnapsackResult (value, selected, DP table)
    stops: list                           # distinct delivery nodes of the selected parcels
    route: list                           # final visiting order [depot, ..., depot]
    route_km: float                       # length of the final route
    nn_route: list                        # route from Nearest Neighbour (before 2-opt)
    nn_km: float
    legs: list = field(default_factory=list)       # (from, to, km, road_path) per leg
    full_path: list = field(default_factory=list)  # every road node visited, in order
    arrivals: dict = field(default_factory=dict)   # stop -> arrival time (hours)
    return_time: float = 0.0                       # time the van is back at the depot
    late_parcels: list = field(default_factory=list)
    dist: dict = field(default_factory=dict)       # shortest distances between depot+stops
    dijkstra_from_depot: tuple = None              # (dist list, prev list) from the depot
    timings: dict = field(default_factory=dict)    # seconds spent in every major step
    used_two_opt: bool = False

    @property
    def selected(self):
        return self.knapsack.selected


def plan_trip(graph, parcels, capacity, depot=DEPOT, trip_no=1,
              start_time=0.0, use_two_opt=False):
    """Plan one trip from the given pool of waiting parcels."""
    timings = {}

    # ---- Step 1: SORT the parcels (earliest deadline, then highest priority) ----
    t = time.perf_counter()
    sorted_parcels = merge_sort(parcels, key=parcel_sort_key)
    timings["sorting"] = time.perf_counter() - t

    # ---- Step 2: KNAPSACK DP picks the best set that fits in the van ----
    t = time.perf_counter()
    kn = knapsack_dp(sorted_parcels, capacity)
    timings["knapsack"] = time.perf_counter() - t

    stops = sorted({p.destination for p in kn.selected})     # distinct delivery points
    nodes = [depot] + stops

    # ---- Step 3: DIJKSTRA from the depot and from every stop ----
    t = time.perf_counter()
    prev_of = {}                          # prev_of[s] = predecessor list of Dijkstra(s)
    dist = {}                             # dist[a][b] = shortest distance a -> b
    depot_result = None
    for s in nodes:
        d_all, p_all = dijkstra(graph, s)
        prev_of[s] = p_all
        dist[s] = {v: d_all[v] for v in nodes}
        if s == depot:
            depot_result = (d_all, p_all)
    timings["dijkstra"] = time.perf_counter() - t

    # ---- Step 4: TSP approximation orders the stops ----
    t = time.perf_counter()
    if stops:
        nn_route, nn_km = nearest_neighbor_route(dist, depot, stops)
    else:
        nn_route, nn_km = [depot], 0.0
    timings["tsp_nn"] = time.perf_counter() - t

    route, km = nn_route, nn_km
    if use_two_opt and stops:
        t = time.perf_counter()
        route, km = two_opt(nn_route, dist)
        timings["two_opt"] = time.perf_counter() - t

    # ---- Build the detailed road path of every leg of the final route ----
    legs, full_path = [], []
    for i in range(len(route) - 1):
        u, v = route[i], route[i + 1]
        path = reconstruct_path(prev_of[u], u, v)
        legs.append((u, v, dist[u][v], path))
        full_path.extend(path if not full_path else path[1:])

    # ---- Arrival times and deadline check ----
    arrivals, elapsed_km = {}, 0.0
    for u, v, km_leg, _ in legs:
        elapsed_km += km_leg
        arrivals.setdefault(v, start_time + elapsed_km / SPEED_KMPH)
    return_time = start_time + elapsed_km / SPEED_KMPH
    late = [p for p in kn.selected if arrivals[p.destination] > p.deadline_hours]

    return TripPlan(
        trip_no=trip_no, start_time=start_time, sorted_parcels=sorted_parcels,
        knapsack=kn, stops=stops, route=route, route_km=km, nn_route=nn_route,
        nn_km=nn_km, legs=legs, full_path=full_path, arrivals=arrivals,
        return_time=return_time, late_parcels=late, dist=dist,
        dijkstra_from_depot=depot_result, timings=timings, used_two_opt=use_two_opt,
    )


def plan_all_trips(graph, parcels, capacity, depot=DEPOT, use_two_opt=False):
    """
    Keep planning trips until no parcel is left.
    Returns (list_of_TripPlan, list_of_undeliverable_parcels).
    A parcel heavier than the whole van can never be delivered.
    """
    undeliverable = [p for p in parcels if p.weight > capacity]
    remaining = [p for p in parcels if p.weight <= capacity]
    trips, start_time, trip_no = [], 0.0, 1

    while remaining:
        plan = plan_trip(graph, remaining, capacity, depot, trip_no, start_time, use_two_opt)
        if not plan.selected:             # safety net: nothing fits -> stop
            break
        trips.append(plan)
        chosen_ids = {p.parcel_id for p in plan.selected}
        remaining = [p for p in remaining if p.parcel_id not in chosen_ids]
        start_time = plan.return_time + LOADING_HOURS     # next trip leaves after re-loading
        trip_no += 1
    return trips, undeliverable
