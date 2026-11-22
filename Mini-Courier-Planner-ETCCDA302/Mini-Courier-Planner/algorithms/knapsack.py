"""0/1 knapsack using dynamic programming."""
def knapsack(parcels, capacity):
    """Maximize parcel value subject to integer weight capacity.

    Returns (selected_parcels, maximum_value, dp_table).
    Each parcel must contain id, weight (kg), and value.
    """
    if capacity < 0:
        raise ValueError("Capacity cannot be negative")
    items = list(parcels)
    if any(p["weight"] < 0 or p["value"] < 0 for p in items):
        raise ValueError("Weights and values must be non-negative")
    n = len(items)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i, parcel in enumerate(items, 1):
        w, v = parcel["weight"], parcel["value"]
        for c in range(capacity + 1):
            dp[i][c] = dp[i-1][c]
            if w <= c:
                dp[i][c] = max(dp[i][c], v + dp[i-1][c-w])
    chosen, c = [], capacity
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i-1][c]:
            chosen.append(items[i-1])
            c -= items[i-1]["weight"]
    chosen.reverse()
    return chosen, dp[n][capacity], dp
