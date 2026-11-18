import csv
import importlib.util
import unittest
from pathlib import Path

import networkx as nx
import numpy as np

PROJECT = Path(__file__).resolve().parents[1]


def read_rows(name):
    with (PROJECT / "data" / name).open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


class ReferenceFigureTests(unittest.TestCase):
    def test_recorded_crop_contains_unique_in_bounds_edges(self):
        edges = set()
        for row in read_rows("ws_reference_crop_edges.csv"):
            points = ((int(row["x1"]), int(row["y1"])),
                      (int(row["x2"]), int(row["y2"])))
            self.assertTrue(all(0 <= coordinate < 20 for point in points for coordinate in point))
            edges.add(tuple(sorted(points)))
        self.assertEqual(len(edges), 1340)

    def test_recorded_distance_normalization_is_preserved(self):
        values = [float(row["reported_proportion"]) for row in read_rows("ws_reference_distance.csv")]
        self.assertEqual(len(values), 11)
        self.assertAlmostEqual(sum(values), 1.000099, places=6)

    def test_rank_counts_reproduce_recorded_fit(self):
        rows = read_rows("wsk_reference_rank_counts.csv")
        rank = np.array([int(row["distance_bin_rank"]) for row in rows])
        counts = np.array([int(row["edge_incidences"]) for row in rows])
        self.assertEqual(counts.sum(), 2 * 27598)
        slope, _ = np.polyfit(np.log(rank), np.log(counts / counts.sum()), 1)
        self.assertAlmostEqual(slope, -1.8125, places=4)

    def test_new_run_excludes_self_pairs_and_uses_separate_output_paths(self):
        modules = []
        for filename in ("watts_strogatz.py", "watts_strogatz_kleinberg.py"):
            spec = importlib.util.spec_from_file_location(filename[:-3], PROJECT / filename)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            modules.append(module)
        distribution = modules[0].calculate_distance_distribution(nx.path_graph(3))
        self.assertNotIn(0, distribution)
        self.assertAlmostEqual(distribution[1], 4 / 6)
        self.assertAlmostEqual(distribution[2], 2 / 6)
        self.assertNotEqual(modules[0].OUTPUT_DIR, modules[1].OUTPUT_DIR)
        self.assertEqual(modules[0].OUTPUT_DIR.parent.name, "runs")
        self.assertEqual(modules[1].OUTPUT_DIR.parent.name, "runs")


if __name__ == "__main__":
    unittest.main()
