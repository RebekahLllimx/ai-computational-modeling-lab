# HW04: PageRank on Web-Google

This implementation computes PageRank from sparse edge-index arrays rather than a dense adjacency matrix. It handles sink nodes, random teleportation, and iterative convergence, then visualizes PageRank against in-degree.

## Data

Download and extract `web-Google.txt.gz` from the [SNAP Web-Google page](https://snap.stanford.edu/data/web-Google.html), then place `web-Google.txt` at:

```text
hw04-pagerank/data/web-Google.txt
```

## Run

Install the root requirements, obtain the dataset above, and run from the repository root:

```bash
python hw04-pagerank/pagerank.py
```

The script processes the full edge list and writes `results/in_degree_vs_pagerank.png` inside this assignment before opening the plot. Set `MPLBACKEND=Agg` for a headless run. For a smaller code-level check, `read_graph()` accepts `max_lines`; the current CLI does not expose that argument.

The recorded full-data run processed 875,713 nodes and 5,105,039 edges. See [analysis.md](analysis.md) for the results and complexity discussion.
