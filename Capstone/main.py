"""
main.py  -  Courier Planning System (command-line demo)
=======================================================
Run:   python main.py                       (default sample: 15 parcels, 12 places, 40 kg van)
       python main.py --two-opt --plot      (also run the 2-opt improvement + draw route map)
       python main.py --parcels 40 --nodes 25 --capacity 60 --seed 7

The program prints an "output trace" for every phase so that it can be copied
into the report as evidence.
"""

import argparse
import os

from data_generator import generate_graph, generate_parcels, load_dataset, save_dataset
from knapsack import format_dp_table, greedy_knapsack
from planner import SPEED_KMPH, plan_all_trips
from shortest_path import reconstruct_path
from sorting import parcel_sort_key

HERE = os.path.dirname(os.path.abspath(__file__))


def banner(text):
    print("\n" + "=" * 92)
    print(text)
    print("=" * 92)


def parcel_table(parcels, graph):
    print("  ID | Destination | Weight(kg) | Deadline(h) | Priority | Value")
    print("  ---+-------------+------------+-------------+----------+------")
    for p in parcels:
        print(f"  {p.parcel_id:>2} | {graph.name(p.destination):<11} | {p.weight:>10} | "
              f"{p.deadline_hours:>11} | {p.priority:>8} | {p.value:>5}")


def path_text(graph, path):
    return " -> ".join(graph.name(n) for n in path)


def main():
    ap = argparse.ArgumentParser(description="Courier planning system")
    ap.add_argument("--parcels", type=int, default=15, help="number of parcels")
    ap.add_argument("--nodes", type=int, default=12, help="number of places (incl. depot)")
    ap.add_argument("--capacity", type=int, default=40, help="van capacity in kg")
    ap.add_argument("--seed", type=int, default=42, help="random seed (same seed = same data)")
    ap.add_argument("--load", type=str, help="load a dataset JSON file instead of generating one")
    ap.add_argument("--two-opt", action="store_true", help="improve each route with 2-opt")
    ap.add_argument("--plot", action="store_true", help="save route map PNG into outputs/")
    ap.add_argument("--save-data", action="store_true", help="save the dataset into data/")
    args = ap.parse_args()

    # ------------------------------------------------------------------ data
    if args.load:
        graph, parcels, capacity = load_dataset(args.load)
    else:
        graph = generate_graph(args.nodes, args.seed)
        parcels = generate_parcels(args.parcels, args.nodes, args.seed)
        capacity = args.capacity
    if args.save_data:
        save_dataset(os.path.join(HERE, "data", "sample_dataset.json"), graph, parcels, capacity)

    banner("PHASE 1 - PROBLEM SETUP")
    print(f"  Road network : {graph.num_nodes} places (1 depot + {graph.num_nodes - 1} customers), "
          f"{graph.num_edges} roads, connected = {graph.is_connected()}")
    print(f"  Parcels      : {len(parcels)} waiting at the depot, total weight "
          f"{sum(p.weight for p in parcels)} kg")
    print(f"  Van capacity : {capacity} kg, average speed {SPEED_KMPH:.0f} km/h")
    print("\n  Waiting parcels (unsorted):")
    parcel_table(parcels, graph)
    print("\n  Road network as adjacency list (distance in km):")
    print(graph.adjacency_text())

    # ------------------------------------------------------------ plan trips
    trips, undeliverable = plan_all_trips(graph, parcels, capacity, use_two_opt=args.two_opt)
    t1 = trips[0]

    # ------------------------------------------------------------- PHASE 2
    banner("PHASE 2 - PACKAGE PRIORITISATION AND BOX FILLING (Trip 1)")
    print("  [2a] Parcels after MERGE SORT (earliest deadline first, then highest priority):")
    parcel_table(t1.sorted_parcels, graph)
    print(f"\n  [2b] Dynamic-programming table for the 0/1 knapsack (capacity {capacity} kg).")
    print("       Cell = best total value using the first i parcels and that capacity.")
    print(format_dp_table(t1.sorted_parcels, t1.knapsack.table, capacity, step=5))
    kn = t1.knapsack
    print(f"\n  [2c] Best value dp[n][{capacity}] = {kn.best_value}")
    print(f"       Selected parcels : {[p.parcel_id for p in kn.selected]}")
    print(f"       Total weight     : {kn.total_weight} kg / {capacity} kg "
          f"({100 * kn.total_weight / capacity:.0f}% full)")
    greedy = greedy_knapsack(t1.sorted_parcels, capacity)
    print(f"       (Comparison: greedy value/weight rule would give value {greedy.best_value}; "
          f"DP gives {kn.best_value})")
    print("\n  Packing plan for Trip 1:")
    parcel_table(kn.selected, graph)

    # ------------------------------------------------------------- PHASE 3
    banner("PHASE 3 - ROUTE MAKER AND GRAPH PROCESSING (Trip 1)")
    print(f"  Delivery points of Trip 1: {[graph.name(s) for s in t1.stops]}")
    d_all, prev = t1.dijkstra_from_depot
    print("\n  [3a] Dijkstra from the Depot - shortest road path to every stop:")
    for s in t1.stops:
        print(f"       Depot -> {graph.name(s):<4} {d_all[s]:7.1f} km   via "
              f"{path_text(graph, reconstruct_path(prev, 0, s))}")

    nodes = [0] + t1.stops
    print("\n  [3b] Shortest-distance matrix between depot and stops (km, from Dijkstra):")
    print("       " + "".join(f"{graph.name(n):>8}" for n in nodes))
    for a in nodes:
        print(f"       {graph.name(a):<6}" + "".join(f"{t1.dist[a][b]:8.1f}" for b in nodes))

    print("\n  [3c] Nearest-Neighbour TSP route:")
    print(f"       {path_text(graph, t1.nn_route)}   = {t1.nn_km:.1f} km")
    if args.two_opt:
        print("       After 2-opt improvement:")
        print(f"       {path_text(graph, t1.route)}   = {t1.route_km:.1f} km")

    print("\n  [3d] Final route, leg by leg:")
    for u, v, km, path in t1.legs:
        print(f"       {graph.name(u):<6} -> {graph.name(v):<6} {km:7.1f} km   road: "
              f"{path_text(graph, path)}")
    print(f"       {'TOTAL ROUTE LENGTH':<22}{t1.route_km:7.1f} km "
          f"(about {t1.route_km / SPEED_KMPH:.1f} h driving)")

    print("\n  [3e] Arrival times and deadline check:")
    for s in t1.route[1:-1]:
        pk = [p for p in kn.selected if p.destination == s]
        for p in pk:
            ok = "on time" if t1.arrivals[s] <= p.deadline_hours else "LATE"
            print(f"       {graph.name(s):<4} parcel {p.parcel_id:>2}: arrive {t1.arrivals[s]:5.2f} h, "
                  f"deadline {p.deadline_hours:>2} h  -> {ok}")

    # ---------------------------------------------------- all trips summary
    banner("ALL TRIPS - COMPLETE DELIVERY PLAN")
    print("  Trip | Parcels (ids)                | Weight | Value | Route (stop order)                | km     | Late")
    print("  -----+------------------------------+--------+-------+-----------------------------------+--------+-----")
    for t in trips:
        ids = ",".join(str(p.parcel_id) for p in t.selected)
        order = ">".join(str(n) for n in t.route)
        print(f"  {t.trip_no:>4} | {ids:<28} | {t.knapsack.total_weight:>6} | {t.knapsack.best_value:>5} | "
              f"{order:<33} | {t.route_km:6.1f} | {len(t.late_parcels):>3}")
    print(f"\n  Trips needed: {len(trips)}   Total distance: {sum(t.route_km for t in trips):.1f} km")
    if undeliverable:
        print(f"  Undeliverable (heavier than the van): {[p.parcel_id for p in undeliverable]}")
    late_all = [(t.trip_no, p.parcel_id) for t in trips for p in t.late_parcels]
    if late_all:
        print(f"  Late parcels (trip, parcel) under the 40 km/h estimate: {late_all}")
        print("  (Later trips depart after earlier trips return, so tight deadlines can be missed -")
        print("   a limitation discussed in the report.)")

    banner("RUNTIME OF MAJOR STEPS (Trip 1, seconds)")
    for step, sec in t1.timings.items():
        print(f"  {step:<10} {sec:.6f}")

    if args.plot:
        from visualize import draw_route_map
        out = os.path.join(HERE, "outputs", "route_map.png")
        draw_route_map(graph, t1, out)
        print(f"\n  Route map saved to {out}")


if __name__ == "__main__":
    main()
