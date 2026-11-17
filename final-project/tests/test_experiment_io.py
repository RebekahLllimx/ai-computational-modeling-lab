import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

import run_experiments
from ca_model import HobbesCA, compute_summary_stats


class ExperimentPersistenceTests(unittest.TestCase):
    def test_saved_metrics_are_numeric_and_pickle_free(self):
        baseline_run = HobbesCA(grid_size=10, b=1.4, seed=1).run(3)
        treated_run = HobbesCA(
            grid_size=10,
            b=1.4,
            p=0.3,
            leviathan_time=1,
            seed=1,
        ).run(3)
        results_a = {1.4: [baseline_run]}
        results_b = {1.4: {0.3: [treated_run]}}
        summary = {
            "A": {1.4: compute_summary_stats([baseline_run])},
            "B": {1.4: {0.3: compute_summary_stats([treated_run])}},
        }
        snapshots = {
            "A": {1.4: {0: np.zeros((2, 2), dtype=np.int8)}},
            "B": {1.4: {0.3: {0: np.ones((2, 2), dtype=np.int8)}}},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            original_output_dir = run_experiments.OUTPUT_DIR
            run_experiments.OUTPUT_DIR = temp_dir
            try:
                run_experiments.save_results(
                    results_a, results_b, summary, snapshots
                )
            finally:
                run_experiments.OUTPUT_DIR = original_output_dir

            with np.load(Path(temp_dir) / "raw_metrics.npz", allow_pickle=False) as raw:
                self.assertIn("A_b1.4_rep0_f_c", raw.files)
                self.assertTrue(all(raw[key].dtype != object for key in raw.files))

            with np.load(Path(temp_dir) / "snapshots.npz", allow_pickle=False) as saved:
                self.assertIn("B_b1.4_p0.3_t0", saved.files)

            metadata = json.loads(
                (Path(temp_dir) / "metadata.json").read_text(encoding="utf-8")
            )
            self.assertIn("intervention_semantics", metadata)


if __name__ == "__main__":
    unittest.main()
