# Phase 1 — Courier Problem Design and Planning

## 1. Problem definition
Mini-Courier Planner selects valuable parcels within a vehicle's weight limit, orders parcels by delivery deadline and priority, computes shortest paths, and constructs a practical delivery tour.

## 2. Inputs and data model
- Parcel: `id`, `weight` (kg), `value` (benefit score), `deadline` (HH:MM), `priority` (1–5), `destination`.
- Delivery network: weighted undirected graph stored as an adjacency dictionary; vertices are depot `W` and delivery points `A`–`D`; edge weights are kilometres.
- Vehicle: maximum capacity 20 kg.

## 3. Algorithm selection
| Requirement | Algorithm | Purpose | Complexity |
|---|---|---|---|
| Parcel ordering | Merge sort | Stable ordering by deadline, then priority | O(n log n) time, O(n) space |
| Compare sorting | Quick sort | Alternative ordering implementation | Average O(n log n), worst O(n²) |
| Packing | 0/1 Knapsack DP | Maximize value within capacity | O(nW) time and space |
| Individual paths | Dijkstra + binary heap | Shortest distance from depot | O((V+E) log V) |
| Multi-stop route | Nearest-neighbor TSP heuristic | Approximate closed delivery tour | O(V²) after pairwise shortest paths |

## 4. Integration flow
1. Load parcel and graph JSON files.
2. Sort parcels by earliest deadline; break ties using descending priority and parcel ID.
3. Run 0/1 Knapsack using the vehicle capacity.
4. Run Dijkstra from the depot to report individual shortest paths.
5. Run nearest-neighbor TSP using shortest-path distances between stops.
6. Print a consolidated plan; benchmark major algorithms separately.

## 5. Assumptions and limitations
- Weights and capacity are integer kilograms for a straightforward DP table.
- Edge weights are non-negative; Dijkstra rejects negative edges.
- The sample graph is connected and symmetric.
- The TSP method is a heuristic and does not guarantee an optimal tour.
- The prototype demonstrates algorithm integration; it does not model live traffic, time windows, or vehicle fleets.
