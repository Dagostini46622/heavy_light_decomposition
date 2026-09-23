import unittest

from heavy_light_decomposition import HeavyLightDecomposition


class TestHeavyLightDecomposition(unittest.TestCase):
    def _build_line(self, n, values=None):
        edges = [(i, i + 1) for i in range(n - 1)]
        return HeavyLightDecomposition(n, edges, root=0, values=values)

    def test_single_vertex(self):
        hld = HeavyLightDecomposition(1, [], root=0, values=[42])
        self.assertEqual(hld.query_path_sum(0, 0), 42)
        self.assertEqual(hld.query_path_max(0, 0), 42)
        hld.update(0, 100)
        self.assertEqual(hld.query_path_sum(0, 0), 100)
        self.assertEqual(hld.query_path_max(0, 0), 100)

    def test_line_sum(self):
        n = 5
        values = [1, 2, 3, 4, 5]
        hld = self._build_line(n, values)
        # Path 0-4 should be sum of all values
        self.assertEqual(hld.query_path_sum(0, 4), 15)
        # Path 1-3
        self.assertEqual(hld.query_path_sum(1, 3), 9)
        # Single vertex path
        self.assertEqual(hld.query_path_sum(2, 2), 3)

    def test_line_max(self):
        n = 6
        values = [10, 5, 8, 20, 3, 7]
        hld = self._build_line(n, values)
        self.assertEqual(hld.query_path_max(0, 5), 20)
        self.assertEqual(hld.query_path_max(1, 4), 20)
        self.assertEqual(hld.query_path_max(3, 3), 20)

    def test_star_tree(self):
        n = 7
        edges = [(0, i) for i in range(1, n)]
        values = [0, 1, 2, 3, 4, 5, 6]
        hld = HeavyLightDecomposition(n, edges, root=0, values=values)
        # Path between two leaves goes through root
        self.assertEqual(hld.query_path_sum(1, 2), 1 + 0 + 2)
        self.assertEqual(hld.query_path_sum(3, 6), 3 + 0 + 6)
        self.assertEqual(hld.query_path_max(1, 5), 5)

    def test_branching_tree(self):
        # Tree:
        #        0
        #       / \
        #      1   2
        #     / \   \
        #    3   4   5
        #   /
        #  6
        n = 7
        edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (3, 6)]
        values = [1, 2, 3, 4, 5, 6, 7]
        hld = HeavyLightDecomposition(n, edges, root=0, values=values)
        self.assertEqual(hld.query_path_sum(6, 5), 7 + 4 + 2 + 1 + 3 + 6)
        self.assertEqual(hld.query_path_sum(4, 2), 5 + 2 + 1 + 3)
        self.assertEqual(hld.query_path_max(6, 4), 7)
        self.assertEqual(hld.query_path_max(2, 5), 6)

    def test_update_sum(self):
        n = 4
        edges = [(0, 1), (1, 2), (2, 3)]
        values = [1, 2, 3, 4]
        hld = HeavyLightDecomposition(n, edges, root=0, values=values)
        hld.update(2, 10)
        self.assertEqual(hld.query_path_sum(0, 3), 1 + 2 + 10 + 4)
        self.assertEqual(hld.query_path_sum(2, 3), 14)

    def test_update_max(self):
        n = 4
        edges = [(0, 1), (1, 2), (2, 3)]
        values = [1, 2, 3, 4]
        hld = HeavyLightDecomposition(n, edges, root=0, values=values)
        hld.update(1, 20)
        self.assertEqual(hld.query_path_max(0, 3), 20)
        hld.update(1, 0)
        self.assertEqual(hld.query_path_max(0, 3), 4)

    def test_disconnected_raises(self):
        n = 4
        edges = [(0, 1), (2, 3)]
        with self.assertRaises(ValueError):
            HeavyLightDecomposition(n, edges, root=0)

    def test_invalid_edge_count(self):
        with self.assertRaises(ValueError):
            HeavyLightDecomposition(3, [(0, 1)], root=0)

    def test_invalid_vertex_index(self):
        with self.assertRaises(ValueError):
            HeavyLightDecomposition(3, [(0, 1), (1, 3)], root=0)

    def test_self_loop_raises(self):
        with self.assertRaises(ValueError):
            HeavyLightDecomposition(2, [(0, 0)], root=0)

    def test_invalid_values_length(self):
        with self.assertRaises(ValueError):
            HeavyLightDecomposition(3, [(0, 1), (1, 2)], root=0, values=[1, 2])

    def test_update_invalid_vertex(self):
        hld = self._build_line(3)
        with self.assertRaises(ValueError):
            hld.update(3, 10)

    def test_query_invalid_vertex(self):
        hld = self._build_line(3)
        with self.assertRaises(ValueError):
            hld.query_path_sum(0, 3)
        with self.assertRaises(ValueError):
            hld.query_path_max(-1, 0)

    def test_all_negative_values(self):
        n = 5
        edges = [(0, 1), (0, 2), (2, 3), (3, 4)]
        values = [-5, -2, -9, -1, -7]
        hld = HeavyLightDecomposition(n, edges, root=0, values=values)
        self.assertEqual(hld.query_path_sum(1, 4), -2 + -5 + -9 + -1 + -7)
        self.assertEqual(hld.query_path_max(1, 4), -1)


if __name__ == "__main__":
    unittest.main()
