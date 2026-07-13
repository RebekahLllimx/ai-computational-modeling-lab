"""
Cellular Automata model for Hobbes's State of Nature.
Spatial evolutionary Prisoner's Dilemma with optional Leviathan (centralized punishment).

Based on Nowak & May (1992) and Gross et al. (2016).
"""

import numpy as np
from scipy.ndimage import convolve, label, maximum_filter
from dataclasses import dataclass
from typing import Optional


@dataclass
class CAMetrics:
    """Metrics for one time step of the CA."""
    f_c: float                # Cooperation fraction
    n_clusters: int           # Number of connected cooperator clusters
    a_max: float              # Largest cluster area (fraction of grid)
    interface_density: float  # C-D boundary length / total possible boundaries


class HobbesCA:
    """
    Spatial evolutionary Prisoner's Dilemma on a 2D square lattice.

    Parameters
    ----------
    grid_size : int
        Side length of the square grid.
    b : float
        Temptation to defect (1 < b <= 2). Payoff matrix: R=1, T=b, P=0, S=0.
    p : float
        Leviathan penalty on defectors (0 = no Leviathan / State of Nature).
    leviathan_time : int or None
        Time step at which Leviathan is introduced. None means never.
    seed : int or None
        Random seed for reproducibility.
    """

    def __init__(
        self,
        grid_size: int = 100,
        b: float = 1.5,
        p: float = 0.0,
        leviathan_time: Optional[int] = None,
        seed: Optional[int] = None,
    ):
        self.grid_size = grid_size
        self.b = b
        self.p = p
        self.leviathan_time = leviathan_time
        self.rng = np.random.default_rng(seed)

        # Initialize grid: 1 = Cooperator, 0 = Defector (50/50 random)
        self.grid = (self.rng.random((grid_size, grid_size)) < 0.5).astype(np.int8)
        self.time = 0
        self._penalty_active = False

        # Pre-compute convolution kernel for counting cooperating neighbors
        self._kernel = np.ones((3, 3), dtype=np.int8)
        self._kernel[1, 1] = 0  # Exclude self from neighbor count

    # ------------------------------------------------------------------
    # Core dynamics
    # ------------------------------------------------------------------

    def step(self) -> np.ndarray:
        """Execute one synchronous update step. Returns the new grid."""
        # --- 1. Count cooperating neighbors (Moore, exclude self) ---
        n_coop = convolve(self.grid.astype(np.float64), self._kernel,
                          mode='wrap', cval=0.0)

        # --- 2. Compute payoffs ---
        # Cooperator payoff = n_coop * R + (8 - n_coop) * S = n_coop (R=1, S=0)
        # Defector   payoff = n_coop * T + (8 - n_coop) * P = n_coop * b (P=0)
        payoff = np.where(self.grid == 1, n_coop, self.b * n_coop)

        # --- 3. Leviathan penalty ---
        if self._penalty_active and self.p > 0:
            payoff[self.grid == 0] -= self.p

        # --- 4. Imitate best in Moore neighborhood (vectorized) ---
        # Build 9 shifted arrays: self first → ties keep current strategy
        H, W = self.grid.shape
        neighbors_payoff = np.empty((9, H, W), dtype=np.float64)
        neighbors_grid = np.empty((9, H, W), dtype=np.int8)

        neighbors_payoff[0] = payoff
        neighbors_grid[0] = self.grid

        idx = 1
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                neighbors_payoff[idx] = np.roll(np.roll(payoff, di, axis=0), dj, axis=1)
                neighbors_grid[idx] = np.roll(np.roll(self.grid, di, axis=0), dj, axis=1)
                idx += 1

        best_idx = np.argmax(neighbors_payoff, axis=0)
        new_grid = np.take_along_axis(neighbors_grid,
                                       best_idx[np.newaxis, :, :], axis=0)[0]

        self.grid = new_grid
        self.time += 1

        # Activate Leviathan at the designated time
        if self.leviathan_time is not None and self.time >= self.leviathan_time:
            self._penalty_active = True

        return self.grid

    def run(self, steps: int, track_metrics: bool = True) -> dict:
        """
        Run the CA for `steps` time steps.

        Returns a dict with time series of metrics if track_metrics=True.
        """
        metrics_ts = {
            'f_c': [], 'n_clusters': [], 'a_max': [],
            'interface_density': [], 'time': [],
        }

        for _ in range(steps):
            self.step()
            if track_metrics:
                m = self.get_metrics()
                metrics_ts['f_c'].append(m.f_c)
                metrics_ts['n_clusters'].append(m.n_clusters)
                metrics_ts['a_max'].append(m.a_max)
                metrics_ts['interface_density'].append(m.interface_density)
                metrics_ts['time'].append(self.time)

        return metrics_ts

    # ------------------------------------------------------------------
    # Metrics (Three Levels of Analysis)
    # ------------------------------------------------------------------

    def get_metrics(self) -> CAMetrics:
        """Compute all three-level metrics for the current grid state."""
        f_c = float(np.mean(self.grid))

        # Connected cooperator clusters (8-connectivity)
        structure = np.ones((3, 3), dtype=int)
        labeled, n_clusters = label(self.grid, structure=structure)

        if n_clusters > 0:
            cluster_sizes = np.bincount(labeled.ravel())[1:]  # exclude background (0)
            a_max = float(np.max(cluster_sizes)) / self.grid.size if len(cluster_sizes) > 0 else 0.0
        else:
            a_max = 0.0

        # Interface density: fraction of adjacent C-D pairs
        interface = 0
        for di, dj in [(0, 1), (1, 0), (1, 1), (-1, 1)]:  # 4 directional pairs
            shifted = np.roll(np.roll(self.grid, di, axis=0), dj, axis=1)
            interface += np.sum(self.grid != shifted)
        # Normalize: max possible interfaces ≈ 4 * grid_size^2
        interface_density = float(interface) / (4 * self.grid.size)

        return CAMetrics(
            f_c=f_c,
            n_clusters=int(n_clusters),
            a_max=a_max,
            interface_density=interface_density,
        )

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def get_snapshot(self) -> np.ndarray:
        """Return a copy of the current grid state."""
        return self.grid.copy()


def compute_summary_stats(metrics_list: list) -> dict:
    """
    Aggregate metrics from multiple runs (list of metric dicts from run()).

    Returns mean and std for each metric at each time step.
    """
    if not metrics_list:
        return {}

    n_runs = len(metrics_list)
    n_steps = len(metrics_list[0]['f_c'])

    summary = {}
    for key in ['f_c', 'n_clusters', 'a_max', 'interface_density']:
        stacked = np.array([m[key] for m in metrics_list])  # (n_runs, n_steps)
        summary[f'{key}_mean'] = np.mean(stacked, axis=0)
        summary[f'{key}_std'] = np.std(stacked, axis=0)
    summary['time'] = metrics_list[0]['time']

    return summary
