# Final project: How does Leviathan change the state of nature?

This project translates a question from Hobbesian political philosophy into a spatial evolutionary game. A cellular automaton places cooperators and defectors on a periodic two-dimensional lattice and compares two conditions:

- **State of nature:** standard spatial Prisoner's Dilemma evolution.
- **Leviathan:** centralized punishment of defectors begins at time step 500.

Five temptation values and three penalty strengths are evaluated with repeated seeded simulations. The intervention is most effective in the intermediate regime (`b = 1.6`), where a fragile coexistence already exists; it cannot recreate cooperation after extinction at `b >= 1.8`.

## Contents

- `report/manuscript.pdf`: anonymized final report.
- `report/manuscript.tex`: anonymized LaTeX source.
- `src/ca_model.py`: cellular-automata model and metrics.
- `src/run_experiments.py`: experimental conditions, repetitions, snapshots, and serialization.
- `src/visualization.py`: figure-generation pipeline.
- `figures/`: the five figures used in the report.

## Run

```bash
cd final-project/src
python run_experiments.py
python visualization.py
```

The full experiment is intentionally substantial: 100 x 100 grids, 1,000 time steps, and repeated parameter combinations. Generated raw arrays and JSON summaries are ignored because they are reproducible and unnecessarily large for source control.

The report preserves its academic bibliography while omitting assigned readings and reference files. Personal name, student number, department, and local paths have been removed.
