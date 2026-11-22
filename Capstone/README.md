# Intelligent Courier Planning System
### ADA Capstone Assignment - Sorting + Dynamic Programming + Dijkstra + TSP Approximation

| | |
|---|---|
| **Student** | Aarush Tyagi |
| **Roll number** | 2501201019 |
| **Programme** | BCA (AI & DS), Section A - K.R. Mangalam University |
| **Course** | Analysis and Design of Algorithms - Capstone (100 marks) |
| **Language** | Python 3 (algorithms use only the standard library) |

A prototype courier planner. Given a list of parcels and a road network it (1) **sorts** the parcels by urgency,
(2) **packs** the van with the most valuable parcels using **dynamic programming**, (3) finds real road distances with
**Dijkstra's algorithm**, and (4) orders the delivery stops with a **nearest-neighbour TSP approximation** (plus optional 2-opt).
A complete PDF version of this report with all source code is in `Capstone_Report.pdf`.

---

## 1. Quick start

```bash
pip install -r requirements.txt                       # only for charts and PDF
python main.py --two-opt --plot --save-data           # demo: full output trace + route map
python main.py --parcels 40 --nodes 25 --capacity 60  # your own size (same seed = same data)
python test_courier.py                                # 12 correctness tests
python performance.py                                 # benchmarks + runtime charts (outputs/)
python make_report_pdf.py                             # rebuild Capstone_Report.pdf
```

### Project structure

| File | Purpose | Phase |
|---|---|---|
| `models.py` | `Parcel` data class and its value formula | 1 |
| `data_generator.py` | reproducible road graphs + parcels, JSON save/load | 1, 4 |
| `sorting.py` | Merge, Quick, Heap and Insertion Sort (from scratch) | 2 |
| `knapsack.py` | 0/1 knapsack DP, backtracking, greedy comparison, DP-table printing | 2 |
| `graph.py` | weighted undirected graph (adjacency list) | 3 |
| `shortest_path.py` | Dijkstra with a min-heap + path reconstruction | 3 |
| `tsp.py` | Nearest Neighbour, 2-opt, brute-force optimum (for testing) | 3, 4 |
| `planner.py` | integrates all algorithms into delivery trips | 1-3 |
| `main.py` | command-line demo that prints the output trace | 5 |
| `visualize.py` | route map picture | 5 |
| `test_courier.py` | 12 automatic tests against reference solutions | 4 |
| `performance.py` | benchmarks and runtime charts | 4 |
| `make_report_pdf.py` | builds the PDF report from the real outputs | 5 |
| `data/sample_dataset.json` | the demonstration dataset | - |
| `outputs/` | output trace, test log, benchmark JSON, charts, route map | 4, 5 |

---

## 2. Phase 1 - Courier problem design and planning

**Problem.** Given parcels, a road graph G = (V, E) with the depot as node 0, and a van capacity C kg, find
(a) the parcels sorted by urgency, (b) the subset for one trip with weight <= C and maximum value,
(c) true shortest road distances between depot and delivery points, (d) a short closed tour Depot -> stops -> Depot.
When parcels remain, the procedure repeats for the next trip.

**Parcel attributes (data design)**

| Attribute | Type | Meaning |
|---|---|---|
| `parcel_id` | int | unique id (also the final sort tie-breaker) |
| `destination` | int | node of the delivery point in the graph |
| `weight` | int, 1-15 kg | weight (integer, because the DP has one column per kg) |
| `deadline_hours` | int, 2-48 | hours until the parcel is due |
| `priority` | int, 1-5 | business importance (5 = express) |
| `value` (derived) | int | `priority*10 + max(0, 48-deadline)//6` - the knapsack objective |

**Graph format.** Undirected weighted graph stored as an **adjacency list** `adj[u] = [(v, km), ...]` (O(V+E) memory; road
networks are sparse - about 1.5 roads per place). Node 0 = depot. Weights are road lengths in km, non-negative (required by
Dijkstra). The generator makes the graph always connected (each new place is linked to its nearest earlier place) and then
adds roads to the two nearest neighbours of every place, so alternative routes exist.

**Algorithm selection**

| Task | Algorithm | Time | Why |
|---|---|---|---|
| Rank parcels | **Merge Sort** (compared with Quick, Heap, Insertion) | O(n log n) | guaranteed bound, stable, supports composite key |
| Choose parcels for one trip | **0/1 Knapsack DP** | O(n*C) | parcels are indivisible; greedy is not always optimal |
| Road distances | **Dijkstra** (min-heap) | O((V+E) log V) | non-negative weights; gives distance + path |
| Order the stops | **Nearest-Neighbour TSP** (+2-opt) | O(k^2) | exact TSP is NP-hard ((k-1)! orders) |

**How they work together**

```
 parcels -> [1 SORT: Merge Sort by deadline, priority]
         -> [2 PACK: knapsack DP picks the best parcels that fit the van]
         -> [3 MEASURE: Dijkstra from depot + every stop -> true distance table + road paths]
         -> [4 ROUTE: nearest-neighbour TSP (+2-opt) orders the stops]
         -> trip plan: route, km, arrival times, deadline check  -> repeat for remaining parcels
```

The sorted order decides how the knapsack considers parcels; on equal total value the DP backtracking prefers earlier (more
urgent) parcels. The knapsack decides which delivery points exist; Dijkstra converts them into a distance matrix that the TSP
heuristic uses, so the route is based on real road distances. See `planner.py`.

**Assumptions:** one van, 40 km/h average speed, 15 min re-loading between trips, two-way roads, a parcel heavier than the van
is reported as undeliverable.

---

## 3. Phase 2 - Package prioritisation and box filling

### 3.1 Sorting (Merge Sort chosen)

Sort key: `(deadline_hours, -priority, parcel_id)`. Four algorithms were written from scratch and compared (every output is
checked against Python's `sorted()` before timing; times in milliseconds, best of 3):

| n parcels | Merge | Quick | Heap | Insertion | built-in sorted() |
|---|---|---|---|---|---|
| 100 | 0.119 | 0.064 | 0.073 | 0.117 | 0.010 |
| 500 | 0.775 | 0.423 | 0.514 | 3.313 | 0.083 |
| 1,000 | 1.694 | 0.971 | 1.169 | 13.951 | 0.192 |
| 2,000 | 3.777 | 2.087 | 2.699 | 57.145 | 0.423 |
| 5,000 | 10.622 | 6.028 | 8.159 | 359.349 | 1.512 |
| 10,000 | 24.388 | 15.073 | 20.677 | skipped | 2.933 |

* Insertion Sort is quadratic: 6.3x slower for n 2,000 -> 5,000 (O(n^2) predicts 6.25x).
* Merge Sort takes 2.30x longer when n doubles from 5,000 to 10,000 (O(n log n) predicts about 2.1x).
* Quick Sort is about 1.6x faster than Merge Sort here, but its worst case is O(n^2) and it is not stable.
* **Merge Sort was chosen** for its guaranteed O(n log n) bound and stability (equal parcels keep their order).
  Python's built-in `sorted()` is far faster because it is written in C; it is only a reference.

Sorted parcels of the demonstration dataset:

```text
  [2a] Parcels after MERGE SORT (earliest deadline first, then highest priority):
  ID | Destination | Weight(kg) | Deadline(h) | Priority | Value
  ---+-------------+------------+-------------+----------+------
  13 | C1          |         13 |           4 |        5 |    57
   6 | C1          |         14 |           6 |        3 |    37
   9 | C4          |          8 |           8 |        2 |    26
  11 | C7          |          9 |           8 |        2 |    26
   3 | C7          |          5 |          12 |        4 |    46
   8 | C8          |          9 |          15 |        2 |    25
  15 | C2          |         13 |          15 |        1 |    15
   2 | C6          |         15 |          21 |        4 |    44
   4 | C8          |          3 |          22 |        2 |    24
   1 | C4          |          3 |          24 |        1 |    14
   7 | C5          |         13 |          29 |        5 |    53
   5 | C9          |         15 |          33 |        3 |    32
  12 | C6          |         15 |          38 |        4 |    41
  10 | C1          |          6 |          41 |        5 |    51
  14 | C6          |          9 |          41 |        2 |    21
```

### 3.2 Box filling - 0/1 knapsack by dynamic programming

`dp[i][c]` = best total value using the first *i* sorted parcels and capacity *c*.

```text
dp[0][c] = 0
dp[i][c] = dp[i-1][c]                                     if weight_i > c
dp[i][c] = max( dp[i-1][c], dp[i-1][c - weight_i] + value_i )   otherwise
```

Backtracking from `dp[n][C]` finds the selected parcels. Time and memory O(n*C). Output for the demo (15 parcels, 40 kg van):

```text
  [2b] Dynamic-programming table for the 0/1 knapsack (capacity 40 kg).
       Cell = best total value using the first i parcels and that capacity.
  row | parcel (w,v)  | c=0   c=5   c=10  c=15  c=20  c=25  c=30  c=35  c=40 
-----------------------------------------------------------------------------
    0 | (no parcels)  | 0     0     0     0     0     0     0     0     0    
    1 | P13 (13,57)   | 0     0     0     57    57    57    57    57    57   
    2 | P6 (14,37)    | 0     0     0     57    57    57    94    94    94   
    3 | P9 (8,26)     | 0     0     26    57    57    83    94    120   120  
    4 | P11 (9,26)    | 0     0     26    57    57    83    109   120   120  
    5 | P3 (5,46)     | 0     46    46    72    103   103   129   155   166  
    6 | P8 (9,25)     | 0     46    46    72    103   103   129   155   166  
    7 | P15 (13,15)   | 0     46    46    72    103   103   129   155   166  
    8 | P2 (15,44)    | 0     46    46    72    103   103   129   155   166  
    9 | P4 (3,24)     | 0     46    70    72    103   127   153   164   179  
   10 | P1 (3,14)     | 0     46    70    84    110   141   153   167   185  
   11 | P7 (13,53)    | 0     46    70    84    110   141   153   180   194  
   12 | P5 (15,32)    | 0     46    70    84    110   141   153   180   194  
   13 | P12 (15,41)   | 0     46    70    84    110   141   153   180   194  
   14 | P10 (6,51)    | 0     46    75    121   135   161   192   204   231  
   15 | P14 (9,21)    | 0     46    75    121   135   161   192   204   231  

  [2c] Best value dp[n][40] = 231
       Selected parcels : [13, 3, 4, 7, 10]
       Total weight     : 40 kg / 40 kg (100% full)
       (Comparison: greedy value/weight rule would give value 218; DP gives 231)

  Packing plan for Trip 1:
  ID | Destination | Weight(kg) | Deadline(h) | Priority | Value
  ---+-------------+------------+-------------+----------+------
  13 | C1          |         13 |           4 |        5 |    57
   3 | C7          |          5 |          12 |        4 |    46
   4 | C8          |          3 |          22 |        2 |    24
   7 | C5          |         13 |          29 |        5 |    53
  10 | C1          |          6 |          41 |        5 |    51

========================================================================
```

**Result:** Trip 1 loads parcels 13, 3, 4, 7, 10 - 40 kg (100 % full), value **231**. The greedy value/weight rule would only
reach 218, which is why DP is needed.

---

## 4. Phase 3 - Route maker and graph processing

* **Graph representation:** adjacency list, 12 places and 17 roads in the demo (full list printed in `outputs/sample_output.txt`).
* **Dijkstra:** from the depot and from every delivery point of the trip. The shortest way between two stops may pass through
  another place (e.g. C8 -> C1 goes through the depot, 65.2 km).
* **TSP:** nearest neighbour from the depot, always to the closest unvisited stop, then back to the depot.

![Route map of trip 1](outputs/route_map.png)

```text
  Delivery points of Trip 1: ['C1', 'C5', 'C7', 'C8']

  [3a] Dijkstra from the Depot - shortest road path to every stop:
       Depot -> C1      49.5 km   via Depot -> C1
       Depot -> C5      60.0 km   via Depot -> C2 -> C5
       Depot -> C7      60.6 km   via Depot -> C2 -> C7
       Depot -> C8      15.7 km   via Depot -> C8

  [3b] Shortest-distance matrix between depot and stops (km, from Dijkstra):
          Depot      C1      C5      C7      C8
       Depot      0.0    49.5    60.0    60.6    15.7
       C1        49.5     0.0    21.7    70.9    65.2
       C5        60.0    21.7     0.0    49.2    75.7
       C7        60.6    70.9    49.2     0.0    76.3
       C8        15.7    65.2    75.7    76.3     0.0

  [3c] Nearest-Neighbour TSP route:
       Depot -> C8 -> C1 -> C5 -> C7 -> Depot   = 212.4 km
       After 2-opt improvement:
       Depot -> C8 -> C1 -> C5 -> C7 -> Depot   = 212.4 km

  [3d] Final route, leg by leg:
       Depot  -> C8        15.7 km   road: Depot -> C8
       C8     -> C1        65.2 km   road: C8 -> Depot -> C1
       C1     -> C5        21.7 km   road: C1 -> C5
       C5     -> C7        49.2 km   road: C5 -> C2 -> C7
       C7     -> Depot     60.6 km   road: C7 -> C2 -> Depot
       TOTAL ROUTE LENGTH      212.4 km (about 5.3 h driving)

  [3e] Arrival times and deadline check:
       C8   parcel  4: arrive  0.39 h, deadline 22 h  -> on time
       C1   parcel 13: arrive  2.02 h, deadline  4 h  -> on time
       C1   parcel 10: arrive  2.02 h, deadline 41 h  -> on time
       C5   parcel  7: arrive  2.57 h, deadline 29 h  -> on time
       C7   parcel  3: arrive  3.80 h, deadline 12 h  -> on time

========================================================================
```

**Final route Trip 1:** `Depot -> C8 -> C1 -> C5 -> C7 -> Depot` = **212.4 km** (about 5.3 h). All five parcels arrive before their deadline.

Complete plan for all parcels:

```text
  Trip | Parcels (ids)                | Weight | Value | Route (stop order)                | km     | Late
  -----+------------------------------+--------+-------+-----------------------------------+--------+-----
     1 | 13,3,4,7,10                  |     40 |   231 | 0>8>1>5>7>0                       |  212.4 |   0
     2 | 6,9,2,1                      |     40 |   121 | 0>6>1>4>0                         |  207.2 |   2
     3 | 11,5,12                      |     39 |    99 | 0>9>6>7>0                         |  134.5 |   1
     4 | 8,15,14                      |     31 |    61 | 0>8>6>2>0                         |  156.2 |   1

  Trips needed: 4   Total distance: 710.3 km
  Late parcels (trip, parcel) under the 40 km/h estimate: [(2, 6), (2, 9), (3, 11), (4, 15)]
  (Later trips depart after earlier trips return, so tight deadlines can be missed -
   a limitation discussed in the report.)

========================================================================
```

The first trip is fully on time. Later trips start after the earlier ones return and nearest neighbour only minimises
distance, so 4 parcels are predicted to be late - an honest limitation (see section 6.4).

---

## 5. Phase 4 - Performance testing and optimisation

### 5.1 Correctness evidence (12 / 12 tests pass)

| Component | Test | Reference |
|---|---|---|
| 4 sorting algorithms | sizes 0-300 with duplicates; parcels sorted by key; input unchanged | `sorted()` |
| Merge Sort | stability | positions of equal keys |
| Knapsack DP | 25 datasets x 3 capacities; never overloaded; never worse than greedy | brute force over all subsets |
| Dijkstra | 10 random graphs, all pairs; reconstructed path length = distance | Floyd-Warshall |
| Nearest Neighbour | 30 instances: valid tour, never shorter than optimum | brute-force optimal tour |
| 2-opt | 20 instances: never longer than the input tour | NN tour |
| Pipeline | no parcel planned twice; overweight parcel and empty input handled | invariants |

```text
PASS  test_dijkstra_matches_floyd_warshall
  PASS  test_knapsack_edge_cases
  PASS  test_knapsack_matches_brute_force
  PASS  test_knapsack_never_worse_than_greedy
  PASS  test_merge_sort_is_stable
  PASS  test_nearest_neighbor_valid_and_not_better_than_optimal
  PASS  test_pipeline_edge_cases
  PASS  test_pipeline_end_to_end
  PASS  test_sorting_does_not_modify_input
  PASS  test_sorting_matches_builtin
  PASS  test_sorting_parcels_by_deadline_then_priority
  PASS  test_two_opt_never_worse

12 / 12 tests passed
```

### 5.2 Runtime of the major steps (milliseconds, best of 3, van capacity 100 kg)

| Dataset | Parcels | Places | Sort | Knapsack | Dijkstra | NN-TSP | 2-opt | Total |
|---|---|---|---|---|---|---|---|---|
| Small | 20 | 15 | 0.021 | 0.127 | 0.040 | 0.007 | 0.010 | 0.20 |
| Medium | 200 | 60 | 0.280 | 1.262 | 0.671 | 0.058 | 0.169 | 2.44 |
| Large | 1,000 | 120 | 1.746 | 7.342 | 2.711 | 0.192 | 0.694 | 12.69 |
| X-Large | 3,000 | 250 | 6.178 | 22.822 | 7.496 | 0.405 | 1.352 | 38.25 |
| XX-Large | 8,000 | 400 | 18.878 | 64.268 | 15.458 | 0.479 | 2.378 | 101.46 |

For the largest dataset (8,000 parcels, 400 places) one trip is planned in 101 ms. The knapsack is the
most expensive step (63 %), then sorting (19 %) and Dijkstra (15 %); the TSP steps
are only 3 %.

Knapsack scaling: with C = 100 kg it takes 0.31 ms for n = 50 and 37.8 ms for n = 5,000;
with n = 500 it takes 0.81 ms for C = 25 and 34.7 ms for C = 800 - linear in n and in C, as O(n*C) predicts.

Graph steps in the worst case (every place is a stop):

| Places V | Dijkstra 1 source | Dijkstra from every stop | NN-TSP | 2-opt |
|---|---|---|---|---|
| 20 | 0.006 | 0.120 | 0.023 | 0.070 |
| 50 | 0.015 | 0.782 | 0.103 | 0.405 |
| 100 | 0.030 | 3.364 | 0.407 | 1.813 |
| 150 | 0.048 | 7.973 | 1.017 | 5.402 |
| 200 | 0.063 | 15.205 | 1.992 | 16.930 |
| 300 | 0.230 | 36.668 | 4.416 | 27.387 |

![Runtime charts](outputs/performance_charts.png)

### 5.3 Quality of the approximation

Brute-force optimum vs heuristics on 100 random instances with 8 stops:

| Heuristic | Average excess over optimum | Worst case | Optimal in |
|---|---|---|---|
| Nearest Neighbour | 4.9 % | 24.8 % | 27 / 100 |
| NN + 2-opt | 0.46 % | 12.0 % | 93 / 100 |

On the large datasets 2-opt shortened the tour by 7.3 % - 13.8 % compared with plain nearest neighbour.

### 5.4 Optimisation comments / future improvements

* **Knapsack:** a 1-D rolling array cuts memory to O(C) when only the best value is needed; NumPy would speed up the inner loop.
* **Sorting:** production code would use the built-in Timsort (C, stable, O(n log n)), about 8x faster than the pure-Python Merge Sort.
* **Dijkstra:** only the depot and the stops are used as sources; results could be cached across trips or Floyd-Warshall precomputed for a fixed map.
* **TSP:** Or-opt, Christofides (1.5-approximation) or a time-window aware heuristic.
* **Deadlines across trips:** a joint multi-trip model would avoid the late parcels seen in later trips.
* **Extensions:** several vans, parcel volume, live traffic weights.

---

## 6. Phase 5 - Final report and demonstration

### 6.1 Result explanation

The demo has 15 parcels (150 kg) but the van holds 40 kg, so **4 trips (710.3 km in total)** are needed. In Trip 1 the sort puts
parcel 13 (due in 4 h, priority 5) first; the DP picks the five parcels with the highest total value that exactly fill the van
(value 231) for customers C1, C5, C7, C8; Dijkstra gives the real road paths (e.g. Depot -> C2 -> C5 = 60.0 km); nearest
neighbour orders the stops C8, C1, C5, C7, giving **212.4 km** and on-time delivery of every parcel.

### 6.2 Evidence in this repository

| Evidence | File |
|---|---|
| Output trace of the demo | `outputs/sample_output.txt` |
| Test log | `outputs/test_results.txt` |
| Benchmark numbers | `outputs/benchmark_results.json`, `outputs/performance_log.txt` |
| Runtime charts | `outputs/performance_charts.png` (+ `chart_*.png`) |
| Route map (screenshot-style evidence) | `outputs/route_map.png` |
| Demonstration dataset | `data/sample_dataset.json` |
| Submission PDF with source code | `Capstone_Report.pdf` |

### 6.3 Marking-scheme checklist

| Phase | What was delivered |
|---|---|
| 1 Design (20) | problem statement, attribute table, graph format, algorithm table with complexity, integration flow (section 2) |
| 2 Sorting + DP (20) | 4 sorting algorithms compared, Merge Sort chosen, DP table, backtracking, selected parcels, packing plan (section 3) |
| 3 Graph + route (20) | adjacency-list graph, Dijkstra paths/matrix, nearest-neighbour route, route length (section 4) |
| 4 Testing (20) | 12 tests vs references, runtimes for small and large inputs, charts, quality study, optimisation notes (section 5) |
| 5 Report + demo (20) | this README, PDF report, output traces, route map, runnable demo, originality statement |

### 6.4 Limitations

Single van and constant speed; nearest neighbour ignores deadlines (some later-trip parcels are predicted late); the road network
is synthetic (distances from coordinates) rather than real map data; integer weights are required by the DP.
All code was written for this assignment with detailed comments, and every number in this report was produced by the code in this repository
(timings depend on the computer; rerun `python performance.py` to reproduce).

## 7. Conclusion

Sorting prioritises the parcels, dynamic programming fills the van optimally, Dijkstra supplies true road distances and a TSP
approximation produces a short route - four algorithm families solving one realistic logistics task. Tests confirm correctness against
independent solutions and the benchmarks confirm the theoretical complexities.
