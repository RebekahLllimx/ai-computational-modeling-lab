# Final project: How does Leviathan change the state of nature?

This project translates a question from Hobbesian political philosophy into a spatial evolutionary game. A cellular automaton places cooperators and defectors on a periodic two-dimensional lattice and compares two conditions:

- **State of nature:** standard spatial Prisoner's Dilemma evolution.
- **Leviathan:** centralized punishment of defectors begins at time step 500.

Five temptation values and three penalty strengths are evaluated with repeated seeded simulations. The intervention is most effective in the intermediate regime (`b = 1.6`), where a fragile coexistence already exists; it cannot recreate cooperation after extinction at `b >= 1.8`.

## Contents

- `report/manuscript.pdf`: final report.
- `report/manuscript.tex`: LaTeX source.
- `src/ca_model.py`: cellular-automata model and metrics.
- `src/run_experiments.py`: experimental conditions, repetitions, snapshots, and serialization.
- `src/visualization.py`: figure-generation pipeline.
- `figures/`: the five figures used in the report.

## Run

For a small, deterministic check from the repository root:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s final-project/tests -v
python final-project/src/quick_demo.py
```

The quick run uses a 20 x 20 grid for 20 steps and does not reproduce the paper's figures. Cluster count and largest-cluster area now use periodic 8-neighbor connectivity, consistent with the evolution rule. Previously saved figures and report values were produced before this correction and have **not** been recalculated. Cooperation fraction and the evolution rule are unaffected; cluster count and largest-cluster area can change where clusters cross a boundary.

To regenerate the original full experiment with the corrected metrics:

```bash
cd final-project/src
python run_experiments.py
python visualization.py
```

The full experiment is intentionally substantial: 100 x 100 grids, 1,000 time steps, and repeated parameter combinations. Generated raw arrays and JSON summaries are ignored because they are reproducible and unnecessarily large for source control.

The report preserves its academic bibliography while omitting assigned readings and external reference files.
