# Heavy Light Decomposition

Heavy Light Decomposition partitions a rooted tree into heavy paths and light edges so that any root-to-node path decomposes into O(log n) contiguous segments, enabling efficient path queries and updates.

## Usage

```python
from heavy_light_decomposition import HeavyLightDecomposition

# Tree with 6 vertices, edges undirected
n = 6
edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5)]
values = [1, 2, 3, 4, 5, 6]

hld = HeavyLightDecomposition(n, edges, root=0, values=values)

print(hld.query_path_sum(3, 5))  # Sum of values on path 3-1-0-2-5
print(hld.query_path_max(3, 5))  # Maximum value on that path

hld.update(1, 20)
print(hld.query_path_sum(3, 5))  # Updated sum
```

## Why this library exists

Path queries on trees (sum, max, etc.) are common in competitive programming and in systems that model hierarchical data. A naive traversal is O(n) per query. Heavy Light Decomposition reduces each query to O(log n) segments by arranging vertices so that heavy paths are contiguous, allowing a Fenwick tree or segment tree to answer each segment in O(log n) time. The total query time is O(log^2 n), and point updates are O(log n).

The trade-off made here is simplicity over absolute optimality: a Fenwick tree handles sums, and a separate segment tree handles maximums. This keeps the code straightforward while still achieving logarithmic complexity. The implementation uses an iterative DFS to avoid recursion limits on large trees.

## Edge cases

The constructor validates that the input edges form a tree on exactly n vertices. If the edge count is not n-1, or the graph is disconnected, or a vertex index is out of range, or a self-loop is present, a `ValueError` is raised. Vertex values are integers, and all operations work correctly with negative values. The maximum query on a path with only negative values returns the largest (closest to zero) value, not some sentinel.
