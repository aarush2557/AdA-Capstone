"""Run with: python -m tests.test_performance"""
import csv, random, time
from pathlib import Path
from algorithms.sorting import merge_sort, quick_sort
from algorithms.knapsack import knapsack
from algorithms.dijkstra import dijkstra

OUT = Path(__file__).resolve().parents[1] / "results"
def timed(fn, *args):
    start = time.perf_counter(); fn(*args)
    return time.perf_counter() - start

def main():
    random.seed(42)
    sort_rows, knap_rows, graph_rows = [], [], []
    for n in [100, 500, 1000, 2000]:
        data = [{"id":f"P{i}","deadline":f"{random.randrange(8,19):02d}:{random.randrange(60):02d}",
                 "priority":random.randrange(1,6),"weight":random.randrange(1,10),"value":random.randrange(1,30)}
                for i in range(n)]
        sort_rows.append([n, timed(merge_sort,data), timed(quick_sort,data)])
    for n in [20, 50, 100, 200]:
        items = [{"id":str(i),"weight":random.randrange(1,11),"value":random.randrange(1,50)} for i in range(n)]
        knap_rows.append([n, timed(knapsack,items,100)])
    for n in [50, 100, 200, 400]:
        graph = {str(i):{str(j):random.randrange(1,30) for j in range(n) if j != i and random.random()<0.08} for i in range(n)}
        for node in graph:
            for neighbor, weight in list(graph[node].items()):
                graph.setdefault(neighbor, {}).setdefault(node, weight)
        graph_rows.append([n, timed(dijkstra,graph,"0")])
    OUT.mkdir(exist_ok=True)
    for name, header, rows in [
        ("sorting_performance.csv",["n","merge_sort_seconds","quick_sort_seconds"],sort_rows),
        ("knapsack_performance.csv",["parcel_count","seconds"],knap_rows),
        ("dijkstra_performance.csv",["vertices","seconds"],graph_rows)]:
        with (OUT/name).open("w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(header); w.writerows(rows)
    print("Benchmark CSV files saved in results/")
if __name__ == "__main__": main()
