"""
sorting.py  (Phase 2 - Package Prioritisation)
==============================================
Contains FOUR sorting algorithms written from scratch (no built-in sort is used
inside them) so that we can compare them in Phase 4:

    merge_sort      O(n log n) always, STABLE, needs O(n) extra memory   <-- CHOSEN
    quick_sort      O(n log n) on average, O(n^2) worst case, not stable
    heap_sort       O(n log n) always, in-place, not stable
    insertion_sort  O(n^2) worst/average, O(n) best case, stable

WHY MERGE SORT IS THE "BEST" CHOICE FOR PARCELS
-----------------------------------------------
1. Guaranteed O(n log n) - the running time never explodes, whatever the input.
2. Stable - parcels with the same sort key keep their original order, which is
   fair and predictable for a courier company.
3. Works naturally with a custom key (deadline, then priority).

Every function has the same signature:   sort(items, key=...) -> new sorted list.
The original list is never modified.
"""

import random


# ---------------------------------------------------------------------------
# The sorting rule for parcels
# ---------------------------------------------------------------------------
def parcel_sort_key(parcel):
    """
    Returns the tuple used to compare two parcels.

    1) earliest deadline first            (deadline_hours ascending)
    2) if deadlines are equal -> higher priority first (-priority ascending)
    3) if still equal -> smaller parcel_id first (makes the order unique)

    Python compares tuples element by element, so this gives exactly that rule.
    """
    return (parcel.deadline_hours, -parcel.priority, parcel.parcel_id)


def _identity(x):
    """Default key: the item itself (used for sorting plain numbers)."""
    return x


# ---------------------------------------------------------------------------
# 1. MERGE SORT  (divide and conquer)
# ---------------------------------------------------------------------------
def merge_sort(items, key=_identity):
    """
    Divide the list into two halves, sort each half recursively, then MERGE the
    two sorted halves into one sorted list.

    Recurrence: T(n) = 2 T(n/2) + O(n)   ->   T(n) = O(n log n)
    """
    # Base case: a list with 0 or 1 element is already sorted.
    if len(items) <= 1:
        return list(items)

    mid = len(items) // 2
    left = merge_sort(items[:mid], key)    # sort the left half
    right = merge_sort(items[mid:], key)   # sort the right half
    return _merge(left, right, key)        # combine them


def _merge(left, right, key):
    """Merge two already-sorted lists into a single sorted list in O(n) time."""
    merged = []
    i = j = 0                              # i walks over left, j walks over right
    while i < len(left) and j < len(right):
        # '<=' (not '<') is what makes merge sort STABLE: on a tie we take the
        # element from the left half first, i.e. the one that came earlier.
        if key(left[i]) <= key(right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    # One of the halves is finished; copy whatever is left of the other half.
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


# ---------------------------------------------------------------------------
# 2. QUICK SORT  (randomised pivot, in-place)
# ---------------------------------------------------------------------------
def quick_sort(items, key=_identity):
    """
    Pick a pivot, move smaller elements to its left and larger to its right,
    then sort the two sides recursively.

    A RANDOM pivot makes the O(n^2) worst case extremely unlikely.
    """
    # "Decorate": store (key, item) pairs so we compute each key only once.
    pairs = [(key(x), x) for x in items]
    _quick_sort_inplace(pairs, 0, len(pairs) - 1)
    return [item for _, item in pairs]     # "undecorate"


def _quick_sort_inplace(a, lo, hi):
    # Loop on the larger part, recurse on the smaller part. This keeps the
    # recursion depth at O(log n) even in unlucky cases.
    while lo < hi:
        p = _partition(a, lo, hi)
        if p - lo < hi - p:
            _quick_sort_inplace(a, lo, p - 1)
            lo = p + 1
        else:
            _quick_sort_inplace(a, p + 1, hi)
            hi = p - 1


def _partition(a, lo, hi):
    """Lomuto partition scheme with a random pivot. Returns the pivot's final index."""
    r = random.randint(lo, hi)             # choose a random pivot position
    a[r], a[hi] = a[hi], a[r]              # move the pivot to the end
    pivot = a[hi][0]
    i = lo                                 # i = boundary of the "smaller" zone
    for j in range(lo, hi):
        if a[j][0] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]              # put the pivot between the two zones
    return i


# ---------------------------------------------------------------------------
# 3. HEAP SORT  (uses a max-heap stored inside the list itself)
# ---------------------------------------------------------------------------
def heap_sort(items, key=_identity):
    """
    Step 1: turn the list into a MAX-HEAP (largest element at index 0).
    Step 2: repeatedly swap the largest element to the end and repair the heap.
    """
    a = [(key(x), x) for x in items]
    n = len(a)
    # Build the heap: start from the last parent node and sift each one down.
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(a, i, n)
    # Extract the maximum one by one.
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]        # biggest goes to its final place
        _sift_down(a, 0, end)              # heap now has 'end' elements
    return [item for _, item in a]


def _sift_down(a, root, size):
    """Push a[root] down until the max-heap property is restored."""
    while True:
        child = 2 * root + 1               # left child
        if child >= size:
            break                          # root has no children -> done
        if child + 1 < size and a[child + 1][0] > a[child][0]:
            child += 1                     # right child is bigger -> use it
        if a[root][0] >= a[child][0]:
            break                          # heap property already holds
        a[root], a[child] = a[child], a[root]
        root = child


# ---------------------------------------------------------------------------
# 4. INSERTION SORT  (simple, fast only for very small lists)
# ---------------------------------------------------------------------------
def insertion_sort(items, key=_identity):
    """Take each element and insert it into its correct place in the sorted prefix."""
    a = [(key(x), x) for x in items]
    for i in range(1, len(a)):
        current = a[i]
        j = i - 1
        # Shift bigger elements one step to the right.
        while j >= 0 and a[j][0] > current[0]:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = current
    return [item for _, item in a]


# A dictionary so that other files (performance.py, tests) can loop over all of them.
SORTING_ALGORITHMS = {
    "Merge Sort": merge_sort,
    "Quick Sort": quick_sort,
    "Heap Sort": heap_sort,
    "Insertion Sort": insertion_sort,
}


def sort_parcels(parcels):
    """The sort used by the courier system: Merge Sort on (deadline, -priority, id)."""
    return merge_sort(parcels, key=parcel_sort_key)
