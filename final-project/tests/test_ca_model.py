import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ca_model import HobbesCA


class PeriodicMetricsTests(unittest.TestCase):
    def setUp(self):
        self.ca = HobbesCA(grid_size=5, seed=42)

    def metrics_for(self, positions):
        self.ca.grid[:] = 0
        for row, col in positions:
            self.ca.grid[row, col] = 1
        return self.ca.get_metrics()

    def test_opposite_edges_are_connected(self):
        metrics = self.metrics_for([(0, 2), (4, 2)])
        self.assertEqual(metrics.n_clusters, 1)
        self.assertAlmostEqual(metrics.a_max, 2 / 25)

    def test_wrapped_diagonal_corners_are_connected(self):
        metrics = self.metrics_for([(0, 0), (4, 4)])
        self.assertEqual(metrics.n_clusters, 1)
        self.assertAlmostEqual(metrics.a_max, 2 / 25)

    def test_distinct_interior_clusters_remain_distinct(self):
        metrics = self.metrics_for([(0, 0), (2, 2)])
        self.assertEqual(metrics.n_clusters, 2)

    def test_empty_and_full_grid(self):
        empty = self.metrics_for([])
        self.assertEqual((empty.f_c, empty.n_clusters, empty.a_max), (0.0, 0, 0.0))
        self.ca.grid[:] = 1
        full = self.ca.get_metrics()
        self.assertEqual((full.f_c, full.n_clusters, full.a_max), (1.0, 1, 1.0))

    def test_seed_reproduces_evolution(self):
        first = HobbesCA(grid_size=20, b=1.6, p=0.3, leviathan_time=5, seed=42)
        second = HobbesCA(grid_size=20, b=1.6, p=0.3, leviathan_time=5, seed=42)
        self.assertEqual(first.run(12), second.run(12))
        np.testing.assert_array_equal(first.get_snapshot(), second.get_snapshot())


if __name__ == "__main__":
    unittest.main()
