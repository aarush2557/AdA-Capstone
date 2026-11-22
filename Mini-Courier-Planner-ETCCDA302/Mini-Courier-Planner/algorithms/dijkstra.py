"""Dijkstra shortest paths for a non-negative weighted graph."""
import heapq

def dijkstra(graph, start):
    if start not in graph:
        raise KeyError(f"Unknown start node: {start}")
    distances = {node: float("inf") for node in graph}
    previous = {node: None for node in graph}
    distances[start] = 0
    queue = [(0, start)]
    while queue:
        dist, node = heapq.heappop(queue)
        if dist != distances[node]:
            continue
        for neighbor, weight in graph[node].items():
            if weight < 0:
                raise ValueError("Dijkstra requires non-negative edge weights")
            candidate = dist + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                previous[neighbor] = node
                heapq.heappush(queue, (candidate, neighbor))
    return distances, previous

def reconstruct_path(previous, target):
    if target not in previous:
        raise KeyError(f"Unknown target node: {target}")
    path, node = [], target
    while node is not None:
        path.append(node)
        node = previous[node]
    return list(reversed(path))
