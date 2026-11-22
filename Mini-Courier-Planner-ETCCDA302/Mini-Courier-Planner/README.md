# Mini-Courier Planner
**ETCCDA302 — Design & Analysis of Algorithms | K.R. Mangalam University**

A Python capstone prototype integrating sorting, dynamic programming, graph algorithms and approximation techniques.

## Requirements
- Python 3.9+
- No third-party packages required for the application or unit tests.
- Matplotlib is optional and only needed to regenerate the performance chart.

## Run on Windows PowerShell
```powershell
cd "D:\vs code\Mini-Courier-Planner"
python main.py
python -m unittest discover -s tests -v
python -m tests.test_performance
```

## Project structure
```text
Mini-Courier-Planner/
├── algorithms/          # sorting, knapsack, Dijkstra, TSP
├── data/                # sample parcels and weighted graph (JSON)
├── docs/                # final report
├── results/             # benchmark CSV files and chart
├── screenshots/         # demonstration evidence
├── tests/               # correctness and performance tests
├── config.py
├── main.py
├── PHASE1_DESIGN.md
├── PHASE4_PERFORMANCE_ANALYSIS.md
└── README.md
```

## Algorithm summary
| Component | Algorithm | Complexity |
|---|---|---|
| Parcel sorting | Merge Sort | O(n log n) |
| Alternative sort | Quick Sort | Average O(n log n), worst O(n²) |
| Packing | 0/1 Knapsack DP | O(nW) |
| Shortest paths | Dijkstra with heap | O((V+E) log V) |
| Delivery tour | Nearest-neighbor TSP heuristic | O(V²) after shortest-path preprocessing |

## Important notes
- `weight` and knapsack `capacity` are integer kilograms.
- Graph edge weights are non-negative kilometres.
- TSP is an approximation and may not return the globally optimal route.
- Benchmark times vary by computer; regenerate them on the machine used for evaluation.
- Fill in student name, roll number, and any required dates in `docs/FINAL_REPORT.md`.
- Capture genuine screenshots during your own run and add them to `screenshots/` before final submission.
