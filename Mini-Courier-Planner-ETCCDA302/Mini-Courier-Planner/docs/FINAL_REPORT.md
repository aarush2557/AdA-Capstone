# Mini-Courier Planner — Final Capstone Report

**K.R. Mangalam University, Gurugram, Haryana**  
**Course:** Analysis & Design of Algorithms 
**Programme:** BCA(AI&DS)  
**Section:** A
**Faculty:** Ruchi Sharma
**Student:** Aarush Tyagi  **Roll No.:** 2501201019

## Abstract
This project demonstrates an integrated courier-planning prototype. It prioritizes parcels, selects a high-value feasible load, calculates shortest paths on a weighted graph, and constructs an approximate multi-stop delivery tour.

## Implemented components
1. Merge Sort and Quick Sort for deadline/priority ordering.
2. 0/1 Knapsack dynamic programming for vehicle packing.
3. Dijkstra's algorithm for shortest paths.
4. Nearest-neighbor TSP approximation for the delivery tour.

## Sample demonstration
With the bundled sample data and 20 kg capacity, the optimal packing component selects parcels based on their value and weight. The graph component reports shortest paths from depot `W`; the tour component returns a closed route beginning and ending at `W`. Run `python main.py` to see the exact output for the included data.

## Testing
Unit tests cover both sorting implementations, knapsack selection, Dijkstra path reconstruction, TSP closure, and rejection of negative edges. Run `python -m unittest discover -s tests -v`.

## Performance
Run `python -m tests.test_performance` to create CSV benchmarks for increasing input sizes. The generated chart and CSVs are stored under `results/`.

## Limitations and future work
The TSP route is approximate, not guaranteed optimal. Future work can add time-window constraints, live road data, multi-vehicle planning, persistence, and a 2-opt improvement pass.

## Conclusion
The prototype combines core algorithm-design techniques in a single executable application and provides reproducible tests and performance measurements.
