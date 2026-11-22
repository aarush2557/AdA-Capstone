"""
performance.py  (Phase 4 - Performance Testing and Optimisation)
================================================================
Measures the runtime of every major step for small and large inputs and draws
the runtime charts used in the report.

    python performance.py          -> runs all experiments (about 1-2 minutes)

Outputs (in outputs/):
    benchmark_results.json    all measured numbers
    chart_sorting.png, chart_knapsack.png, chart_graph.png, chart_pipeline.png
    performance_charts.png    the four charts in one picture
"""

import json
import os
import random
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data_generator import generate_graph, generate_parcels
from knapsack import knapsack_dp
from planner import plan_trip
from shortest_path import dijkstra
from sorting import SORTING_ALGORITHMS, parcel_sort_key
from tsp import brute_force_tsp, nearest_neighbor_route, two_opt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")


def timed(fn, repeats=3):
    """Run fn() several times and return the BEST (smallest) time in seconds.
    The minimum is the least disturbed by other programs running on the computer."""
    best = float("inf")
    for _ in range(repeats):
        t = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - t)
    return best


# ---------------------------------------------------------------- experiment 1
def bench_sorting():
    sizes = [100, 500, 1000, 2000, 5000, 10000]
    results = {name: [] for name in SORTING_ALGORITHMS}
    results["Python sorted() (reference)"] = []
    for n in sizes:
        parcels = generate_parcels(n, 50, seed=1)
        expected = sorted(parcels, key=parcel_sort_key)
        for name, fn in SORTING_ALGORITHMS.items():
            if name == "Insertion Sort" and n > 5000:
                results[name].append(None)            # too slow, skip (O(n^2))
                continue
            out = fn(parcels, key=parcel_sort_key)
            assert out == expected                    # correctness check inside the benchmark
            results[name].append(timed(lambda: fn(parcels, key=parcel_sort_key)))
        results["Python sorted() (reference)"].append(
            timed(lambda: sorted(parcels, key=parcel_sort_key)))
    return {"sizes": sizes, "times": results}


# ---------------------------------------------------------------- experiment 2
def bench_knapsack():
    # (a) grow the number of parcels, capacity fixed at 100 kg
    sizes = [50, 100, 200, 500, 1000, 2000, 5000]
    by_n = [timed(lambda p=generate_parcels(n, 30, 1): knapsack_dp(p, 100)) for n in sizes]
    # (b) grow the capacity, number of parcels fixed at 500
    caps = [25, 50, 100, 200, 400, 800]
    parcels = generate_parcels(500, 30, 1)
    by_w = [timed(lambda c=c: knapsack_dp(parcels, c)) for c in caps]
    return {"sizes": sizes, "time_by_n": by_n, "capacities": caps, "time_by_capacity": by_w}


# ---------------------------------------------------------------- experiment 3
def bench_graph():
    sizes = [20, 50, 100, 150, 200, 300]
    single, all_sources, nn, opt2 = [], [], [], []
    for v in sizes:
        g = generate_graph(v, seed=7)
        stops = list(range(1, v))                     # worst case: visit EVERY place
        nodes = [0] + stops
        single.append(timed(lambda: dijkstra(g, 0)))

        def all_dijkstra():
            d = {}
            for s in nodes:
                row, _ = dijkstra(g, s)
                d[s] = {t: row[t] for t in nodes}
            return d
        all_sources.append(timed(all_dijkstra, repeats=2))
        dist = all_dijkstra()
        nn.append(timed(lambda: nearest_neighbor_route(dist, 0, stops)))
        route, _ = nearest_neighbor_route(dist, 0, stops)
        opt2.append(timed(lambda: two_opt(route, dist), repeats=1))
    return {"sizes": sizes, "dijkstra_single": single, "dijkstra_all_sources": all_sources,
            "tsp_nn": nn, "two_opt": opt2}


# ---------------------------------------------------------------- experiment 4
def bench_pipeline():
    """Full one-trip pipeline on datasets of growing size (van capacity 100 kg)."""
    configs = [("Small", 20, 15), ("Medium", 200, 60), ("Large", 1000, 120),
               ("X-Large", 3000, 250), ("XX-Large", 8000, 400)]
    rows = []
    for label, n_parcels, n_nodes in configs:
        g = generate_graph(n_nodes, seed=11)
        parcels = generate_parcels(n_parcels, n_nodes, seed=11)
        best = None
        for _ in range(3):                            # repeat, keep run with smallest total
            plan = plan_trip(g, parcels, 100, use_two_opt=True)
            if best is None or sum(plan.timings.values()) < sum(best.timings.values()):
                best = plan
        rows.append({"label": label, "parcels": n_parcels, "nodes": n_nodes,
                     "selected": len(best.selected), "stops": len(best.stops),
                     "route_km": round(best.route_km, 1), "nn_km": round(best.nn_km, 1),
                     "timings": best.timings})
    return rows


# ---------------------------------------------------------------- experiment 5
def quality_experiment(instances=100, stops_count=8):
    """How far is Nearest Neighbour from the TRUE optimum? (brute force, 8 stops)"""
    nn_ratio, opt_ratio = [], []
    for seed in range(instances):
        g = generate_graph(16, seed)
        stops = random.Random(seed).sample(range(1, 16), stops_count)
        nodes = [0] + stops
        dist = {}
        for s in nodes:
            row, _ = dijkstra(g, s)
            dist[s] = {t: row[t] for t in nodes}
        route, nn_len = nearest_neighbor_route(dist, 0, stops)
        _, better = two_opt(route, dist)
        _, optimal = brute_force_tsp(dist, 0, stops)
        nn_ratio.append(nn_len / optimal)
        opt_ratio.append(better / optimal)
    avg = lambda xs: sum(xs) / len(xs)
    return {"instances": instances, "stops": stops_count,
            "nn_avg_ratio": avg(nn_ratio), "nn_max_ratio": max(nn_ratio),
            "nn_optimal_count": sum(r < 1 + 1e-9 for r in nn_ratio),
            "two_opt_avg_ratio": avg(opt_ratio), "two_opt_max_ratio": max(opt_ratio),
            "two_opt_optimal_count": sum(r < 1 + 1e-9 for r in opt_ratio)}


# ------------------------------------------------------------------- charts
def draw_sorting(ax, d):
    for name, times in d["times"].items():
        xs = [s for s, t in zip(d["sizes"], times) if t is not None]
        ys = [t for t in times if t is not None]
        style = "--" if "sorted()" in name else "-"
        ax.plot(xs, ys, style, marker="o", label=name)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_title("Sorting parcels: runtime vs number of parcels")
    ax.set_xlabel("number of parcels n"); ax.set_ylabel("time (seconds)")
    ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=8)


def draw_knapsack(ax, d):
    # Both experiments plotted against the SIZE OF THE DP TABLE (n x W cells).
    # If the time is O(n*W), all points lie on one straight line.
    cells_n = [n * 100 for n in d["sizes"]]                  # capacity fixed at 100
    cells_w = [500 * w for w in d["capacities"]]             # n fixed at 500
    ax.plot(cells_n, d["time_by_n"], marker="o", label="vary n (W = 100 kg)")
    ax.plot(cells_w, d["time_by_capacity"], marker="s", label="vary W (n = 500)")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_title("0/1 Knapsack DP: time vs DP-table size (n x W)")
    ax.set_xlabel("table cells = n x W"); ax.set_ylabel("time (seconds)")
    ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=8)


def draw_graph(ax, d):
    ax.plot(d["sizes"], d["dijkstra_single"], marker="o", label="Dijkstra (1 source)")
    ax.plot(d["sizes"], d["dijkstra_all_sources"], marker="o", label="Dijkstra (from every stop)")
    ax.plot(d["sizes"], d["tsp_nn"], marker="o", label="Nearest-Neighbour TSP")
    ax.plot(d["sizes"], d["two_opt"], marker="o", label="2-opt improvement")
    ax.set_yscale("log")
    ax.set_title("Graph steps: runtime vs number of places (all visited)")
    ax.set_xlabel("number of places V (= stops + depot)"); ax.set_ylabel("time (seconds)")
    ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=8)


def draw_pipeline(ax, rows):
    steps = ["sorting", "knapsack", "dijkstra", "tsp_nn", "two_opt"]
    names = ["Sorting", "Knapsack DP", "Dijkstra", "NN-TSP", "2-opt"]
    width = 0.16
    for k, (step, nm) in enumerate(zip(steps, names)):
        xs = [i + (k - 2) * width for i in range(len(rows))]
        ax.bar(xs, [r["timings"].get(step, 0) for r in rows], width, label=nm)
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([f'{r["label"]}\n{r["parcels"]} parcels' for r in rows], fontsize=8)
    ax.set_yscale("log")
    ax.set_title("One-trip pipeline: time of each major step")
    ax.set_ylabel("time (seconds, log scale)"); ax.grid(alpha=0.3, axis="y", which="both")
    ax.legend(fontsize=8, ncol=2)


def save_charts(res):
    drawers = [("sorting", draw_sorting, res["sorting"]), ("knapsack", draw_knapsack, res["knapsack"]),
               ("graph", draw_graph, res["graph"]), ("pipeline", draw_pipeline, res["pipeline"])]
    for name, fn, data in drawers:                    # each chart as its own picture
        fig, ax = plt.subplots(figsize=(7, 4.5))
        fn(ax, data)
        fig.tight_layout(); fig.savefig(os.path.join(OUT, f"chart_{name}.png"), dpi=150)
        plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))  # and all four together
    for ax, (name, fn, data) in zip(axes.flat, drawers):
        fn(ax, data)
    fig.suptitle("Courier Planner - runtime of the major steps", fontsize=15)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "performance_charts.png"), dpi=130)
    plt.close(fig)


def main():
    res = {}
    for name, fn in [("sorting", bench_sorting), ("knapsack", bench_knapsack),
                     ("graph", bench_graph), ("pipeline", bench_pipeline),
                     ("quality", quality_experiment)]:
        t = time.perf_counter()
        res[name] = fn()
        print(f"  experiment '{name}' finished in {time.perf_counter() - t:.1f} s")
    with open(os.path.join(OUT, "benchmark_results.json"), "w") as f:
        json.dump(res, f, indent=2)
    save_charts(res)
    print("  results and charts saved in outputs/")


if __name__ == "__main__":
    main()
