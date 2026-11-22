"""
knapsack.py  (Phase 2 - Box Filling using Dynamic Programming)
==============================================================
Problem: the delivery van can carry at most `capacity` kg. Each parcel has a
weight and a value (importance). Choose the set of parcels for ONE trip so that
the total weight <= capacity and the total value is as LARGE as possible.

This is the classic 0/1 KNAPSACK problem ("0/1" because a parcel is either
taken completely or not at all - we cannot cut a parcel in half).

DP IDEA
-------
Let dp[i][c] = the best total value we can get using ONLY the first i parcels
and a van of capacity c.

    dp[0][c] = 0                                   (no parcels -> no value)
    dp[i][c] = dp[i-1][c]                          if parcel i is too heavy
    dp[i][c] = max( dp[i-1][c],                    skip parcel i
                    dp[i-1][c - w_i] + v_i )       take parcel i

Time  : O(n * capacity)        Space : O(n * capacity)
The answer is dp[n][capacity]. To find WHICH parcels were taken we walk the
table backwards (backtracking).
"""

from dataclasses import dataclass, field


@dataclass
class KnapsackResult:
    """Everything the knapsack returns, so the caller can print evidence."""
    best_value: int                      # maximum total value
    selected: list                       # parcels chosen for the trip
    total_weight: int                    # their combined weight
    table: list = field(repr=False, default_factory=list)   # the full DP table


def knapsack_dp(parcels, capacity):
    """Solve the 0/1 knapsack with bottom-up dynamic programming."""
    n = len(parcels)

    # dp has (n+1) rows and (capacity+1) columns, all initially 0.
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    # ---- fill the table row by row ----
    for i in range(1, n + 1):
        w = parcels[i - 1].weight        # weight of the i-th parcel
        v = parcels[i - 1].value         # value of the i-th parcel
        for c in range(capacity + 1):
            dp[i][c] = dp[i - 1][c]                        # option 1: skip it
            if w <= c:                                     # option 2: take it (if it fits)
                take = dp[i - 1][c - w] + v
                if take > dp[i][c]:
                    dp[i][c] = take

    # ---- backtrack to find which parcels were taken ----
    selected = []
    c = capacity
    for i in range(n, 0, -1):
        # If the value changed between row i-1 and row i, parcel i must have been taken.
        # (On ties we do NOT take the parcel, which favours the EARLIER parcels in the
        #  list. Because the list is sorted by deadline, urgent parcels win ties.)
        if dp[i][c] != dp[i - 1][c]:
            selected.append(parcels[i - 1])
            c -= parcels[i - 1].weight
    selected.reverse()                   # restore the original (sorted) order

    return KnapsackResult(
        best_value=dp[n][capacity],
        selected=selected,
        total_weight=sum(p.weight for p in selected),
        table=dp,
    )


def greedy_knapsack(parcels, capacity):
    """
    A simple GREEDY alternative used only for comparison: take parcels in order of
    value/weight ratio while they fit. It is fast but NOT always optimal - this
    is exactly why the assignment asks for Dynamic Programming.
    """
    ordered = sorted(parcels, key=lambda p: p.value / p.weight, reverse=True)
    chosen, weight_used, total_value = [], 0, 0
    for p in ordered:
        if weight_used + p.weight <= capacity:
            chosen.append(p)
            weight_used += p.weight
            total_value += p.value
    return KnapsackResult(total_value, chosen, weight_used)


def format_dp_table(parcels, table, capacity, step=5):
    """
    Return the DP table as printable text. Showing every column would be too wide,
    so only the columns 0, step, 2*step, ... capacity are displayed.
    """
    columns = list(range(0, capacity + 1, step))
    if columns[-1] != capacity:
        columns.append(capacity)

    lines = []
    header = "  row | parcel (w,v)  | " + " ".join(f"c={c:<3}" for c in columns)
    lines.append(header)
    lines.append("-" * len(header))
    for i, row in enumerate(table):
        if i == 0:
            label = "(no parcels)"
        else:
            p = parcels[i - 1]
            label = f"P{p.parcel_id} ({p.weight},{p.value})"
        cells = " ".join(f"{row[c]:<5}" for c in columns)
        lines.append(f"  {i:>3} | {label:<13} | {cells}")
    return "\n".join(lines)
