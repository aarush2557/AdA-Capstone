"""
Courier Planning System - ADA Capstone

"""

DEPOT = 0           
USE_TIME = False     

# operation counters used for the performance test
OPS = {"sort": 0, "knapsack": 0, "route": 0}


# HELPER FUNCTIONS 

SEED = [12345]


def set_seed(value):
    SEED[0] = value


def rand_int(low, high):
    """Simple linear congruential generator -> integer between low and high."""
    SEED[0] = (SEED[0] * 1103515245 + 12345) % 2147483648
    return low + (SEED[0] // 65536) % (high - low + 1)


def heap_push(heap, item):
    """Insert item into a min-heap stored in a list."""
    heap.append(item)
    i = len(heap) - 1
    while i > 0:
        parent = (i - 1) // 2
        if heap[parent] <= heap[i]:
            break
        heap[parent], heap[i] = heap[i], heap[parent]
        i = parent
    OPS["route"] += 1


def heap_pop(heap):
    """Remove and return the smallest item of the min-heap."""
    top = heap[0]
    last = heap.pop()
    if heap:
        heap[0] = last
        i = 0
        n = len(heap)
        while True:
            left, right, small = 2 * i + 1, 2 * i + 2, i
            if left < n and heap[left] < heap[small]:
                small = left
            if right < n and heap[right] < heap[small]:
                small = right
            if small == i:
                break
            heap[i], heap[small] = heap[small], heap[i]
            i = small
    OPS["route"] += 1
    return top


def timer_now():
    """Returns current time in seconds if USE_TIME is on, else 0."""
    if USE_TIME:
        import time
        return time.perf_counter()
    return 0


# PHASE 1 : DATA DESIGN


def parcel_value(p):
    """Value for knapsack: high priority and urgent deadline = more valuable."""
    bonus = 24 - p["deadline"]
    if bonus < 0:
        bonus = 0
    return p["priority"] * 10 + bonus


def add_edge(graph, a, b, w):
    graph[a].append((b, w))
    graph[b].append((a, w))


def make_graph(n, seed):
    """Connected road network with n nodes, distances 1..20 km."""
    set_seed(seed)
    graph = [[] for _ in range(n)]
    for i in range(1, n):                       # chain keeps graph connected
        add_edge(graph, i - 1, i, rand_int(1, 20))
    for _ in range(2 * n):                      # extra random roads
        a = rand_int(0, n - 1)
        b = rand_int(0, n - 1)
        if a != b:
            add_edge(graph, a, b, rand_int(1, 20))
    return graph


def make_parcels(count, n_nodes, seed):
    set_seed(seed + 100)
    parcels = []
    for i in range(count):
        parcels.append({"id": i + 1,
                        "dest": rand_int(1, n_nodes - 1),
                        "weight": rand_int(1, 10),
                        "priority": rand_int(1, 5),
                        "deadline": rand_int(2, 48)})
    return parcels


# PHASE 2 : SORTING + DYNAMIC PROGRAMMING

def comes_first(a, b):
    """True if parcel a should be delivered before (or same as) parcel b."""
    if a["deadline"] != b["deadline"]:
        return a["deadline"] < b["deadline"]
    return a["priority"] >= b["priority"]


def merge_sort(arr):
    """Merge sort, O(n log n): earliest deadline first, then higher priority."""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        OPS["sort"] += 1                       # one comparison
        if comes_first(left[i], right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    while i < len(left):
        result.append(left[i])
        i += 1
    while j < len(right):
        result.append(right[j])
        j += 1
    return result


def knapsack(parcels, capacity):
    """0/1 Knapsack by Dynamic Programming, O(n * capacity).
    dp[i][w] = best value using the first i parcels with weight limit w."""
    n = len(parcels)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        wt = parcels[i - 1]["weight"]
        val = parcel_value(parcels[i - 1])
        for w in range(capacity + 1):
            OPS["knapsack"] += 1               # one table cell filled
            dp[i][w] = dp[i - 1][w]            # option 1: skip parcel i
            if wt <= w:
                take = dp[i - 1][w - wt] + val # option 2: take parcel i
                if take > dp[i][w]:
                    dp[i][w] = take

    # trace back to find which parcels were chosen
    chosen = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            chosen.append(parcels[i - 1])
            w -= parcels[i - 1]["weight"]
    chosen.reverse()
    return dp[n][capacity], chosen, dp


# PHASE 3 : GRAPH PROCESSING

def dijkstra(graph, source):
    """Shortest distance from source to all nodes. Returns (dist, previous)."""
    INF = 999999999
    dist = [INF] * len(graph)
    prev = [None] * len(graph)
    dist[source] = 0
    heap = []
    heap_push(heap, (0, source))

    while len(heap) > 0:
        d, u = heap_pop(heap)
        if d > dist[u]:
            continue                            # outdated entry
        for v, w in graph[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                prev[v] = u
                heap_push(heap, (dist[v], v))
    return dist, prev


def get_path(prev, target):
    path = []
    while target is not None:
        path.append(target)
        target = prev[target]
    path.reverse()
    return path


def closest_stop(unvisited, dist):
    """Return the unvisited stop with the smallest distance."""
    best = None
    for s in unvisited:
        if best is None or dist[s] < dist[best]:
            best = s
    return best


def nearest_neighbour_route(graph, stops):
    """TSP approximation: always go to the closest unvisited stop
    (distances from Dijkstra), then return to the warehouse."""
    unvisited = list(stops)
    order = [DEPOT]
    full_path = [DEPOT]
    total = 0
    current = DEPOT

    while len(unvisited) > 0:
        dist, prev = dijkstra(graph, current)
        nxt = closest_stop(unvisited, dist)
        total += dist[nxt]
        full_path += get_path(prev, nxt)[1:]
        order.append(nxt)
        unvisited.remove(nxt)
        current = nxt

    dist, prev = dijkstra(graph, current)       # return to warehouse
    total += dist[DEPOT]
    full_path += get_path(prev, DEPOT)[1:]
    order.append(DEPOT)
    return order, full_path, total


# FULL SYSTEM

def unique_destinations(parcels):
    stops = []
    for p in parcels:
        if p["dest"] not in stops:
            stops.append(p["dest"])
    return stops


def plan_delivery(parcels, graph, capacity):
    """Runs sorting -> knapsack -> route. Records operation counts (and time)."""
    OPS["sort"] = OPS["knapsack"] = OPS["route"] = 0
    t0 = timer_now()
    sorted_parcels = merge_sort(parcels)
    t1 = timer_now()
    best_value, chosen, dp = knapsack(sorted_parcels, capacity)
    t2 = timer_now()
    order, path, km = nearest_neighbour_route(graph, unique_destinations(chosen))
    t3 = timer_now()
    return {"sorted": sorted_parcels, "value": best_value, "chosen": chosen,
            "dp": dp, "order": order, "path": path, "km": km,
            "ops": (OPS["sort"], OPS["knapsack"], OPS["route"]),
            "ms": ((t1 - t0) * 1000, (t2 - t1) * 1000, (t3 - t2) * 1000)}


# DEMO

def demo():
    n_nodes, capacity = 10, 25
    graph = make_graph(n_nodes, 7)
    parcels = make_parcels(12, n_nodes, 7)

    print("=" * 66)
    print("DEMO: warehouse = node 0, van capacity =", capacity, "kg")
    print("=" * 66)

    print("\nRoad network (node: [(neighbour, km), ...]):")
    for u in range(n_nodes):
        print(" ", u, ":", graph[u])

    print("\nInput parcels:")
    print("  ID  dest  weight  priority  deadline  value")
    for p in parcels:
        print(f"  {p['id']:>2}  {p['dest']:>4}  {p['weight']:>6}  {p['priority']:>8}"
              f"  {p['deadline']:>8}  {parcel_value(p):>5}")

    res = plan_delivery(parcels, graph, capacity)

    print("\nPhase 2 - After Merge Sort (earliest deadline first):")
    for p in res["sorted"]:
        print(f"  parcel {p['id']:>2}  deadline={p['deadline']:>2}h  "
              f"priority={p['priority']}  weight={p['weight']}")

    chosen = res["chosen"]
    print(f"\nPhase 2 - Knapsack DP table, last row (capacity 0..{capacity}):")
    print(" ", res["dp"][-1])
    print("  Best total value  :", res["value"])
    print("  Parcels loaded    :", [p["id"] for p in chosen])
    load = 0
    for p in chosen:
        load += p["weight"]
    print(f"  Load              : {load} / {capacity} kg")
    left = []
    for p in res["sorted"]:
        if p not in chosen:
            left.append(p["id"])
    print("  Left for next trip:", left)

    print("\nPhase 3 - Dijkstra shortest path from warehouse:")
    dist, prev = dijkstra(graph, DEPOT)
    for s in unique_destinations(chosen):
        print(f"  0 -> {s}: {dist[s]} km, path {get_path(prev, s)}")

    print("\nPhase 3 - Nearest-Neighbour route:")
    print("  Stop order  :", " -> ".join([str(x) for x in res["order"]]))
    print("  Full path   :", " -> ".join([str(x) for x in res["path"]]))
    print("  Route length:", res["km"], "km")

    print("\nCorrectness checks:")
    ok_sort = True
    s = res["sorted"]
    for i in range(len(s) - 1):
        if not comes_first(s[i], s[i + 1]):
            ok_sort = False
    ok_route = True
    for stop in unique_destinations(chosen):
        if stop not in res["path"]:
            ok_route = False
    print("  Parcels correctly sorted        :", ok_sort)
    print("  Load within van capacity        :", load <= capacity)
    print("  Route visits every delivery stop:", ok_route)


# PHASE 4 : PERFORMANCE TESTING

def performance_test():
    print("\n" + "=" * 66)
    print("PERFORMANCE TEST (number of basic operations per step)")
    print("=" * 66)
    print(f"{'Parcels':>8}{'Nodes':>7}{'Sort ops':>10}{'Knapsack ops':>14}"
          f"{'Route ops':>11}{'Km':>7}")

    results = []
    for n_parcels, n_nodes in [(50, 30), (100, 60), (200, 100), (500, 200), (1000, 300)]:
        graph = make_graph(n_nodes, 5)
        parcels = make_parcels(n_parcels, n_nodes, 5)
        res = plan_delivery(parcels, graph, n_parcels * 2)
        a, b, c = res["ops"]
        results.append((n_parcels, a, b, c, res["ms"]))
        print(f"{n_parcels:>8}{n_nodes:>7}{a:>10}{b:>14}{c:>11}{res['km']:>7}")

    if USE_TIME:
        print("\nReal time in milliseconds (sort, knapsack, route):")
        for n, a, b, c, ms in results:
            print(f"  {n:>5} parcels: {ms[0]:.3f}  {ms[1]:.3f}  {ms[2]:.3f}")

    print("\nRUNTIME CHART (bar length proportional to operations, # = largest/50)")
    biggest = 0
    for r in results:
        for v in r[1:4]:
            if v > biggest:
                biggest = v
    for n, a, b, c, ms in results:
        print(f"\n  {n} parcels")
        for name, v in (("Sort    ", a), ("Knapsack", b), ("Route   ", c)):
            bars = v * 50 // biggest
            if bars < 1:
                bars = 1
            print(f"    {name} |{'#' * bars} {v}")


if __name__ == "__main__":
    demo()
    performance_test()
