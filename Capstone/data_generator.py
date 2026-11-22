"""
data_generator.py  (Phase 1 - data design / Phase 4 - test datasets)
====================================================================
Creates reproducible test data. Passing the same `seed` always gives the same
dataset, so results in the report can be repeated by anybody.

    generate_graph(num_nodes, seed)    -> road network (Graph)
    generate_parcels(n, num_nodes, seed) -> list of Parcel
    save_dataset / load_dataset        -> JSON files in the data/ folder
"""

import json
import math
import random

from graph import Graph
from models import Parcel


def generate_graph(num_nodes, seed=42, neighbours=2, area=100.0):
    """
    Create a random but always CONNECTED road network inside an area x area km square.

    Step 0: place the depot (node 0) in the centre and the customers randomly.
    Step 1: connect every new node to its nearest earlier node  -> a spanning tree,
            which guarantees that every place can be reached from the depot.
    Step 2: connect every node to its `neighbours` nearest places -> extra roads, so
            there are several alternative routes and Dijkstra has real work to do.
    Road length = straight-line distance in km, rounded to 1 decimal.
    """
    rng = random.Random(seed)
    graph = Graph(num_nodes)

    # Step 0: coordinates
    coords = [(area / 2, area / 2)]                       # depot in the middle
    for _ in range(1, num_nodes):
        coords.append((round(rng.uniform(0, area), 1), round(rng.uniform(0, area), 1)))
    graph.coords = coords

    def road_length(i, j):
        return max(0.1, round(math.dist(coords[i], coords[j]), 1))

    # Step 1: spanning tree
    for i in range(1, num_nodes):
        nearest = min(range(i), key=lambda j: road_length(i, j))
        graph.add_edge(i, nearest, road_length(i, nearest))

    # Step 2: extra roads to the nearest neighbours
    for i in range(num_nodes):
        others = sorted((j for j in range(num_nodes) if j != i),
                        key=lambda j: road_length(i, j))
        for j in others[:neighbours]:
            if not graph.has_edge(i, j):
                graph.add_edge(i, j, road_length(i, j))
    return graph


def generate_parcels(num_parcels, num_nodes, seed=42):
    """
    Create `num_parcels` random parcels going to customers 1..num_nodes-1.
    weight 1-15 kg, deadline 2-48 hours, priority 1-5.
    """
    rng = random.Random(seed + 1000)          # different stream than the graph
    parcels = []
    for pid in range(1, num_parcels + 1):
        parcels.append(Parcel(
            parcel_id=pid,
            destination=rng.randint(1, num_nodes - 1),
            weight=rng.randint(1, 15),
            deadline_hours=rng.randint(2, 48),
            priority=rng.randint(1, 5),
        ))
    return parcels


def save_dataset(path, graph, parcels, capacity):
    """Write graph + parcels + van capacity into one JSON file."""
    data = {
        "capacity_kg": capacity,
        "graph": graph.to_dict(),
        "parcels": [p.to_dict() for p in parcels],
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_dataset(path):
    """Read a JSON file written by save_dataset. Returns (graph, parcels, capacity)."""
    with open(path) as f:
        data = json.load(f)
    graph = Graph.from_dict(data["graph"])
    parcels = [Parcel.from_dict(d) for d in data["parcels"]]
    return graph, parcels, data["capacity_kg"]
