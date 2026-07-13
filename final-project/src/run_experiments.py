"""
Experiment runner for Hobbes Leviathan CA simulation.

Two experimental conditions:
  Condition A — State of Nature (no Leviathan): standard PD evolution
  Condition B — Leviathan introduced at t=500 with penalty p

Parameter adjustments for laptop performance:
  - Grid: 100×100 (original 200×200 reduced for speed)
  - Reps: 5 per parameter combo (original 10 reduced)
"""

import numpy as np
import json
import time
import os
from datetime import datetime
from itertools import product

from ca_model import HobbesCA, compute_summary_stats

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'outputs')

# Parameters (adjusted for laptop performance)
GRID_SIZE = 100        # 100×100 (Nowak & May used 200×200)
TOTAL_STEPS = 1000      # t=0 to t=999
LEVIATHAN_TIME = 500    # Leviathan introduced at t=500
N_REPS = 5              # Repetitions per parameter combo

B_VALUES = [1.2, 1.4, 1.6, 1.8, 2.0]   # Temptation to defect
P_VALUES = [0.1, 0.3, 0.5]              # Leviathan penalty strength
BASE_SEED = 42

# Time points for spatial snapshots
SNAPSHOT_TIMES = [0, 250, 500, 600, 750, 1000]


def run_condition_a(b_values=B_VALUES, n_reps=N_REPS, seed=BASE_SEED):
    """
    Condition A: State of Nature — no Leviathan, standard PD evolution.

    Returns dict: results[b][rep] = metrics_ts
    """
    print("=" * 60)
    print("Condition A: State of Nature (No Leviathan)")
    print("=" * 60)

    results = {}
    total = len(b_values) * n_reps
    current = 0

    for b in b_values:
        results[b] = []
        for rep in range(n_reps):
            current += 1
            t0 = time.time()

            ca = HobbesCA(
                grid_size=GRID_SIZE, b=b, p=0.0,
                leviathan_time=None,  # Never introduce Leviathan
                seed=seed + rep,
            )
            metrics = ca.run(TOTAL_STEPS, track_metrics=True)
            results[b].append(metrics)

            elapsed = time.time() - t0
            f_c_final = metrics['f_c'][-1]
            print(f"  [{current}/{total}] b={b:.1f}, rep={rep+1} | "
                  f"final f_c={f_c_final:.3f} | {elapsed:.1f}s")

    return results


def run_condition_b(b_values=B_VALUES, p_values=P_VALUES,
                    n_reps=N_REPS, seed=BASE_SEED):
    """
    Condition B: Leviathan introduced at t=500 with penalty p.

    Returns dict: results[b][p][rep] = metrics_ts
    """
    print("\n" + "=" * 60)
    print("Condition B: Leviathan Introduced at t=500")
    print("=" * 60)

    results = {}
    total = len(b_values) * len(p_values) * n_reps
    current = 0

    for b in b_values:
        results[b] = {}
        for p in p_values:
            results[b][p] = []
            for rep in range(n_reps):
                current += 1
                t0 = time.time()

                ca = HobbesCA(
                    grid_size=GRID_SIZE, b=b, p=p,
                    leviathan_time=LEVIATHAN_TIME,
                    seed=seed + rep,
                )
                metrics = ca.run(TOTAL_STEPS, track_metrics=True)
                results[b][p].append(metrics)

                elapsed = time.time() - t0
                f_c_final = metrics['f_c'][-1]
                # f_c just before Leviathan
                f_c_pre = metrics['f_c'][LEVIATHAN_TIME - 1]
                print(f"  [{current}/{total}] b={b:.1f}, p={p:.1f}, rep={rep+1} | "
                      f"f_c_pre={f_c_pre:.3f} → f_c_final={f_c_final:.3f} | {elapsed:.1f}s")

    return results


def collect_snapshots(b_values=B_VALUES, p_values=P_VALUES, seed=BASE_SEED):
    """
    Collect spatial snapshots at key time points for a single representative run.
    """
    print("\n" + "=" * 60)
    print("Collecting spatial snapshots")
    print("=" * 60)

    snapshots = {}

    # Condition A: one rep per b
    snapshots['A'] = {}
    for b in b_values:
        ca = HobbesCA(grid_size=GRID_SIZE, b=b, p=0.0,
                      leviathan_time=None, seed=seed)
        snapshots['A'][b] = {}
        for t in range(TOTAL_STEPS + 1):
            if t in SNAPSHOT_TIMES:
                snapshots['A'][b][t] = ca.get_snapshot()
            if t < TOTAL_STEPS:
                ca.step()
        print(f"  A: b={b:.1f} ✓")

    # Condition B: one rep per (b, p)
    snapshots['B'] = {}
    for b in b_values:
        snapshots['B'][b] = {}
        for p in p_values:
            ca = HobbesCA(grid_size=GRID_SIZE, b=b, p=p,
                          leviathan_time=LEVIATHAN_TIME, seed=seed)
            snapshots['B'][b][p] = {}
            for t in range(TOTAL_STEPS + 1):
                if t in SNAPSHOT_TIMES:
                    snapshots['B'][b][p][t] = ca.get_snapshot()
                if t < TOTAL_STEPS:
                    ca.step()
            print(f"  B: b={b:.1f}, p={p:.1f} ✓")

    return snapshots


def summarize_results(results_a, results_b):
    """Compute summary statistics for all conditions."""
    summary = {}

    # Condition A
    summary['A'] = {}
    for b, reps in results_a.items():
        summary['A'][b] = compute_summary_stats(reps)

    # Condition B
    summary['B'] = {}
    for b, p_dict in results_b.items():
        summary['B'][b] = {}
        for p, reps in p_dict.items():
            summary['B'][b][p] = compute_summary_stats(reps)

    return summary


def save_results(results_a, results_b, summary, snapshots):
    """Save all results to disk as compressed numpy arrays and JSON metadata."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save summary as JSON (lightweight)
    summary_json = {}
    for cond in ['A', 'B']:
        summary_json[cond] = {}
        if cond == 'A':
            for b in summary['A']:
                summary_json['A'][str(b)] = {
                    k: v.tolist() if hasattr(v, 'tolist') else v
                    for k, v in summary['A'][b].items()
                }
        else:
            for b in summary['B']:
                summary_json['B'][str(b)] = {}
                for p in summary['B'][b]:
                    summary_json['B'][str(b)][str(p)] = {
                        k: v.tolist() if hasattr(v, 'tolist') else v
                        for k, v in summary['B'][b][p].items()
                    }

    with open(os.path.join(OUTPUT_DIR, 'summary.json'), 'w') as f:
        json.dump(summary_json, f, indent=2)

    # Save raw metrics as npz
    raw = {}
    for b, reps in results_a.items():
        for i, rep in enumerate(reps):
            raw[f'A_b{b}_rep{i}'] = {k: np.array(v) for k, v in rep.items()}
    for b, p_dict in results_b.items():
        for p, reps in p_dict.items():
            for i, rep in enumerate(reps):
                raw[f'B_b{b}_p{p}_rep{i}'] = {k: np.array(v) for k, v in rep.items()}

    np.savez_compressed(os.path.join(OUTPUT_DIR, 'raw_metrics.npz'), **raw)

    # Save snapshots
    np.savez_compressed(os.path.join(OUTPUT_DIR, 'snapshots.npz'),
                        **{f'{cond}_b{b}_p{p}_t{t}': grid
                           for cond, b_dict in snapshots.items()
                           for b, p_dict in b_dict.items()
                           for p, t_dict in (p_dict.items() if cond == 'B' else {'NA': p_dict}.items())
                           for t, grid in t_dict.items()})

    # Metadata
    meta = {
        'timestamp': datetime.now().isoformat(),
        'grid_size': GRID_SIZE,
        'total_steps': TOTAL_STEPS,
        'leviathan_time': LEVIATHAN_TIME,
        'n_reps': N_REPS,
        'b_values': B_VALUES,
        'p_values': P_VALUES,
        'snapshot_times': SNAPSHOT_TIMES,
    }
    with open(os.path.join(OUTPUT_DIR, 'metadata.json'), 'w') as f:
        json.dump(meta, f, indent=2)

    print(f"\nResults saved to {OUTPUT_DIR}/")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    t_start = time.time()

    # Run both conditions
    results_a = run_condition_a()
    results_b = run_condition_b()

    # Collect snapshots
    snapshots = collect_snapshots()

    # Summarize
    summary = summarize_results(results_a, results_b)

    # Save
    save_results(results_a, results_b, summary, snapshots)

    t_total = time.time() - t_start
    print(f"\nTotal time: {t_total:.0f}s ({t_total/60:.1f} min)")
    print("Experiment complete. Run visualization.py to generate plots.")
