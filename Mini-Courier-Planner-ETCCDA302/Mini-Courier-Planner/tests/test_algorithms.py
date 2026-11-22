import unittest
from algorithms.sorting import merge_sort, quick_sort
from algorithms.knapsack import knapsack
from algorithms.dijkstra import dijkstra, reconstruct_path
from algorithms.tsp import nearest_neighbor_tsp

class AlgorithmTests(unittest.TestCase):
    def setUp(self):
        self.parcels = [
            {"id":"P1","deadline":"10:00","priority":1,"weight":8,"value":15},
            {"id":"P2","deadline":"09:00","priority":3,"weight":5,"value":10},
            {"id":"P3","deadline":"09:00","priority":5,"weight":6,"value":12},
        ]
        self.graph = {"W":{"A":10,"B":15},"A":{"W":10,"B":5},"B":{"W":15,"A":5}}
    def test_merge_sort(self):
        self.assertEqual([p["id"] for p in merge_sort(self.parcels)], ["P3","P2","P1"])
    def test_quick_sort(self):
        self.assertEqual([p["id"] for p in quick_sort(self.parcels)], ["P3","P2","P1"])
    def test_knapsack(self):
        chosen, value, table = knapsack(self.parcels, 11)
        self.assertEqual(value, 22)
        self.assertEqual(sum(p["weight"] for p in chosen), 11)
        self.assertEqual(len(table), 4)
    def test_dijkstra(self):
        dist, prev = dijkstra(self.graph, "W")
        self.assertEqual(dist["B"], 15)
        self.assertEqual(reconstruct_path(prev, "B"), ["W","B"])
    def test_tsp(self):
        route, distance = nearest_neighbor_tsp(self.graph, "W")
        self.assertEqual(route[0], "W")
        self.assertEqual(route[-1], "W")
        self.assertEqual(distance, 30)
    def test_negative_edge_rejected(self):
        with self.assertRaises(ValueError):
            dijkstra({"A":{"B":-1},"B":{}}, "A")

if __name__ == "__main__":
    unittest.main()
