# Final project: How does Leviathan change the state of nature?

This project translates a question from Hobbesian political philosophy into a spatial evolutionary game. A cellular automaton places cooperators and defectors on a periodic two-dimensional lattice and compares two conditions:

- **State of nature:** standard spatial Prisoner's Dilemma evolution.
- **Leviathan:** centralized punishment of defectors begins at time step 500.

Five temptation values and three penalty strengths are evaluated with repeated seeded simulations. The intervention is most effective in the intermediate regime (`b = 1.6`), where a fragile coexistence already exists; it cannot recreate cooperation after extinction at `b >= 1.8`.

## Contents

- [Technical report](report/technical_report.md): model, experimental design, and results.
- [Engineering design](docs/ENGINEERING_DESIGN.md): requirements, architecture, interfaces, testing, and technical decisions.
- `src/ca_model.py`: cellular-automata model and metrics.
- `src/run_experiments.py`: experimental conditions, repetitions, snapshots, and serialization.
- `src/visualization.py`: figure-generation pipeline.
- `figures/`: reference figures for the simulation and its results.

## Run

For a small, deterministic check from the repository root:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s final-project/tests -v
python final-project/src/quick_demo.py
```

The quick run uses a 20 x 20 grid for 20 steps. Cluster count and largest-cluster area use periodic eight-neighbor connectivity, consistent with the evolution rule.

At `t = 500`, the control and intervention runs still share the same state. The penalty is applied to the transition from `t = 500` to `t = 501`, so paired trajectories can be compared from an identical pre-intervention history.

To run the full parameter sweep and generate the figures:

```bash
cd final-project/src
python run_experiments.py
python visualization.py
```

The full experiment uses 100 x 100 grids, 1,000 transitions, and five paired seeds (42-46). It runs 25 baseline and 75 intervention trajectories, then collects representative snapshots. Both commands overwrite generated files in `final-project/src/outputs/`; they do not update the committed `figures/current_*.png` files automatically.

The output directory contains `summary.json`, `raw_metrics.npz`, `snapshots.npz`, and `metadata.json`. Visualization reads those files and writes figure PNGs and PDFs into the same directory. Saved metric series cover states `t = 1` through `t = 1000`; the initial state `t = 0` is retained separately among the snapshots. See the [output contract](docs/ENGINEERING_DESIGN.md#persisted-outputs) before consuming arrays or comparing a rerun with the report.
