"""Parcel sorting algorithms: merge sort and quick sort."""
def _key(parcel):
    # Earlier deadline first; higher priority breaks ties.
    return (parcel["deadline"], -parcel["priority"], parcel["id"])

def merge_sort(parcels):
    items = list(parcels)
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left, right = merge_sort(items[:mid]), merge_sort(items[mid:])
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if _key(left[i]) <= _key(right[j]):
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    return result + left[i:] + right[j:]

def quick_sort(parcels):
    """Three-way quicksort; returns a new list and handles duplicate keys."""
    items = list(parcels)
    if len(items) < 2:
        return items
    pivot = _key(items[len(items)//2])
    low, equal, high = [], [], []
    for item in items:
        k = _key(item)
        if k < pivot: low.append(item)
        elif k > pivot: high.append(item)
        else: equal.append(item)
    return quick_sort(low) + equal + quick_sort(high)
