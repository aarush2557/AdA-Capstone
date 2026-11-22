"""Integrated Mini-Courier Planner demonstration."""
import json
from pathlib import Path
from config import VEHICLE_CAPACITY_KG, DEPOT
from algorithms.sorting import merge_sort, quick_sort
from algorithms.knapsack import knapsack
from algorithms.dijkstra import dijkstra, reconstruct_path
from algorithms.tsp import nearest_neighbor_tsp

ROOT = Path(__file__).resolve().parent

def load_data():
    with (ROOT / "data" / "parcels.json").open(encoding="utf-8") as f:
        parcels = json.load(f)
    with (ROOT / "data" / "locations.json").open(encoding="utf-8") as f:
        locations = json.load(f)
    return parcels, locations

def main():
    parcels, graph = load_data()
    print("=" * 62)
    print("              MINI-COURIER PLANNER")
    print("=" * 62)
    print("\n1) PARCEL PRIORITIZATION")
    for label, result in [("Merge sort", merge_sort(parcels)), ("Quick sort", quick_sort(parcels))]:
        print(f"{label}: " + ", ".join(p["id"] for p in result))
    print("\n2) OPTIMAL BOX FILLING (0/1 KNAPSACK)")
    selected, value, _ = knapsack(parcels, VEHICLE_CAPACITY_KG)
    weight = sum(p["weight"] for p in selected)
    print(f"Capacity: {VEHICLE_CAPACITY_KG} kg | Selected: {', '.join(p['id'] for p in selected)}")
    print(f"Packed weight: {weight} kg | Total value: {value}")
    print("\n3) SHORTEST PATHS (DIJKSTRA)")
    distances, previous = dijkstra(graph, DEPOT)
    for node in sorted(graph):
        print(f"{DEPOT} -> {node}: {distances[node]} km | Path: {' -> '.join(reconstruct_path(previous, node))}")
    print("\n4) DELIVERY TOUR (NEAREST-NEIGHBOR TSP APPROXIMATION)")
    route, length = nearest_neighbor_tsp(graph, DEPOT)
    print("Route:", " -> ".join(route))
    print(f"Total tour distance: {length} km")
    print("\nPlanning complete.")

if __name__ == "__main__":
    main()
