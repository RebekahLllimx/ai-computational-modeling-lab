# HW03: Small-world networks

This assignment implements two related spatial network models:

- `watts_strogatz.py`: rewires an eight-neighbor periodic lattice and measures shortest-path and clustering behavior.
- `watts_strogatz_kleinberg.py`: adds distance-dependent long-range links and fits a power-law relationship between rank and connection probability.

The recorded 10,000-node Watts-Strogatz experiment produced an average path length of 6.45 and average clustering coefficient of 0.3171 at rewiring probability 0.1. The WSK experiment estimated `q = 1.8125` under its specified sampling and fitting procedure.

```bash
python watts_strogatz.py
python watts_strogatz_kleinberg.py
```

Both programs are computationally expensive at the default 100 x 100 scale. Outputs are written to `results/`; selected reference outputs are included. Assigned article PDFs are cited in the repository but not redistributed.
