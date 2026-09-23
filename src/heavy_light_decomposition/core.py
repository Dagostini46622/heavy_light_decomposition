"""Core implementation of Heavy Light Decomposition.

Heavy Light Decomposition (HLD) partitions a rooted tree into heavy paths and
light edges so that any root-to-node path decomposes into O(log n) segments.
This module provides a class that builds the decomposition and answers path
queries on vertex values in logarithmic time.

This implementation supports two types of path queries:
- path_sum: sum of vertex values along a path
- path_max: maximum vertex value along a path

It also supports point updates of vertex values.

The underlying data structure is a Fenwick tree for sums and a segment tree
for maximum values, both built over the heavy-path ordering. This avoids any
third-party dependencies and keeps the code self-contained.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple, Union


class FenwickTree:
    """Fenwick tree for prefix sums and point updates."""

    def __init__(self, size: int) -> None:
        self.size = size
        self.tree = [0] * (size + 1)

    def add(self, idx: int, delta: int) -> None:
        """Add delta to position idx (1-indexed)."""
        while idx <= self.size:
            self.tree[idx] += delta
            idx += idx & -idx

    def sum(self, idx: int) -> int:
        """Prefix sum up to position idx (1-indexed)."""
        res = 0
        while idx > 0:
            res += self.tree[idx]
            idx -= idx & -idx
        return res

    def range_sum(self, left: int, right: int) -> int:
        """Sum on inclusive 1-indexed range [left, right]."""
        return self.sum(right) - self.sum(left - 1)


class SegmentTreeMax:
    """Segment tree for range maximum and point updates."""

    def __init__(self, data: Sequence[int]) -> None:
        self.n = len(data)
        self.size = 1
        while self.size < self.n:
            self.size <<= 1
        self.tree = [-(10**18)] * (2 * self.size)
        for i, val in enumerate(data):
            self.tree[self.size + i] = val
        for i in range(self.size - 1, 0, -1):
            self.tree[i] = max(self.tree[2 * i], self.tree[2 * i + 1])

    def update(self, idx: int, value: int) -> None:
        """Set value at 0-indexed position idx."""
        pos = idx + self.size
        self.tree[pos] = value
        pos //= 2
        while pos:
            self.tree[pos] = max(self.tree[2 * pos], self.tree[2 * pos + 1])
            pos //= 2

    def query(self, left: int, right: int) -> int:
        """Maximum on inclusive 0-indexed range [left, right]."""
        left += self.size
        right += self.size
        res = -(10**18)
        while left <= right:
            if left % 2 == 1:
                res = max(res, self.tree[left])
                left += 1
            if right % 2 == 0:
                res = max(res, self.tree[right])
                right -= 1
            left //= 2
            right //= 2
        return res


class HeavyLightDecomposition:
    """Heavy Light Decomposition for a rooted tree with vertex values.

    The tree is given as a list of edges and a root. Vertex indices are
    0-based. Values are integers. The decomposition orders vertices so that
    heavy paths appear contiguously, enabling path queries via segment trees.

    Attributes:
        n: number of vertices
        parent: parent of each vertex, -1 for root
        depth: depth from root
        heavy: heavy child of each vertex, -1 if none
        head: head of the heavy path containing each vertex
        pos: position in the decomposition order
        values: current vertex values
    """

    def __init__(self, n: int, edges: Sequence[Tuple[int, int]], root: int = 0, values: Union[Sequence[int], None] = None) -> None:
        """Initialize decomposition.

        Args:
            n: number of vertices, indexed 0..n-1.
            edges: list of (u, v) undirected edges. Must form a tree.
            root: root vertex for decomposition.
            values: initial vertex values. If None, all zeros.

        Raises:
            ValueError: if edges do not form a tree on n vertices, or if any
                vertex index is out of range, or if values length is not n.
        """
        if n <= 0:
            raise ValueError("n must be positive")
        if len(edges) != n - 1:
            raise ValueError("edges must form a tree (n-1 edges)")
        if values is not None and len(values) != n:
            raise ValueError("values must have length n")
        for u, v in edges:
            if not (0 <= u < n and 0 <= v < n):
                raise ValueError("vertex index out of range")
            if u == v:
                raise ValueError("self-loops are not allowed")

        self.n = n
        self.root = root
        self.parent = [-1] * n
        self.depth = [0] * n
        self.heavy = [-1] * n
        self.size = [0] * n
        self.head = [0] * n
        self.pos = [0] * n
        self.values = list(values) if values is not None else [0] * n

        # Build adjacency list
        adj: List[List[int]] = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        # First DFS to compute parent, depth, subtree sizes, heavy child
        stack: List[Tuple[int, int, int]] = [(root, -1, 0)]
        order: List[int] = []
        while stack:
            v, p, state = stack.pop()
            if state == 0:
                self.parent[v] = p
                self.depth[v] = self.depth[p] + 1 if p != -1 else 0
                stack.append((v, p, 1))
                for u in adj[v]:
                    if u != p:
                        stack.append((u, v, 0))
            else:
                order.append(v)
                sz = 1
                max_child_size = 0
                heavy_child = -1
                for u in adj[v]:
                    if u != p:
                        sz += self.size[u]
                        if self.size[u] > max_child_size:
                            max_child_size = self.size[u]
                            heavy_child = u
                self.size[v] = sz
                self.heavy[v] = heavy_child

        # Verify tree connectivity
        if len(order) != n:
            raise ValueError("edges do not form a connected tree")

        # Second DFS to assign positions and heads, decomposing heavy paths first
        cur_pos = 0
        stack = [(root, root)]
        while stack:
            v, h = stack.pop()
            # Follow heavy path from v
            while v != -1:
                self.head[v] = h
                self.pos[v] = cur_pos
                cur_pos += 1
                # Push light children for later processing
                for u in adj[v]:
                    if u != self.parent[v] and u != self.heavy[v]:
                        stack.append((u, u))
                v = self.heavy[v]

        # Build underlying data structures
        decomposed_values = [0] * n
        for v in range(n):
            decomposed_values[self.pos[v]] = self.values[v]

        self.fenwick = FenwickTree(n)
        for i, val in enumerate(decomposed_values):
            self.fenwick.add(i + 1, val)

        self.segment_max = SegmentTreeMax(decomposed_values)

    def update(self, vertex: int, value: int) -> None:
        """Update value of a single vertex."""
        if not (0 <= vertex < self.n):
            raise ValueError("vertex index out of range")
        pos = self.pos[vertex]
        delta = value - self.values[vertex]
        self.values[vertex] = value
        self.fenwick.add(pos + 1, delta)
        self.segment_max.update(pos, value)

    def query_path_sum(self, u: int, v: int) -> int:
        """Return sum of vertex values on path u-v."""
        self._check_vertex(u)
        self._check_vertex(v)
        res = 0
        while self.head[u] != self.head[v]:
            if self.depth[self.head[u]] < self.depth[self.head[v]]:
                u, v = v, u
            res += self.fenwick.range_sum(self.pos[self.head[u]] + 1, self.pos[u] + 1)
            u = self.parent[self.head[u]]
        if self.depth[u] > self.depth[v]:
            u, v = v, u
        res += self.fenwick.range_sum(self.pos[u] + 1, self.pos[v] + 1)
        return res

    def query_path_max(self, u: int, v: int) -> int:
        """Return maximum vertex value on path u-v."""
        self._check_vertex(u)
        self._check_vertex(v)
        res = -(10**18)
        while self.head[u] != self.head[v]:
            if self.depth[self.head[u]] < self.depth[self.head[v]]:
                u, v = v, u
            res = max(res, self.segment_max.query(self.pos[self.head[u]], self.pos[u]))
            u = self.parent[self.head[u]]
        if self.depth[u] > self.depth[v]:
            u, v = v, u
        res = max(res, self.segment_max.query(self.pos[u], self.pos[v]))
        return res

    def _check_vertex(self, vertex: int) -> None:
        if not (0 <= vertex < self.n):
            raise ValueError("vertex index out of range")
