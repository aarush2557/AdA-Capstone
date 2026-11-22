# Phase 4 — Performance Testing and Optimization

Run `python -m tests.test_performance` to regenerate the CSV benchmark files. The benchmark uses deterministic random seed 42 and records elapsed wall-clock seconds with `time.perf_counter()`.

## Test sizes
- Sorting: 100, 500, 1,000, 2,000 parcels; Merge Sort and Quick Sort.
- Knapsack: 20, 50, 100, 200 parcels at capacity 100.
- Dijkstra: 50, 100, 200, 400 vertices on sparse random graphs.

## Interpretation
Sorting should scale near O(n log n) for merge sort and average-case quick sort. Knapsack runtime grows with both parcel count and capacity (O(nW)). Dijkstra depends on vertices and edges (O((V+E) log V)).

## Optimization opportunities
1. Use a binary heap (already used) rather than scanning all unsettled vertices.
2. Compress the knapsack DP to one dimension when the full table is not needed; iterate capacity downward.
3. Use a better TSP heuristic (2-opt/local search) or exact solvers for small instances.
4. Cache shortest-path results when the same graph is queried repeatedly.
5. Benchmark multiple repetitions and report medians for more stable measurements.

Actual timings are machine-dependent; consult the CSV files generated on the submission computer rather than treating sample timings as universal.
