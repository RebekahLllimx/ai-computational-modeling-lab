# HW04: PageRank on Web-Google

This implementation computes PageRank from sparse edge-index arrays rather than a dense adjacency matrix. It handles sink nodes, random teleportation, and iterative convergence, then visualizes PageRank against in-degree.

## Data

Download and extract `web-Google.txt.gz` from the [SNAP Web-Google page](https://snap.stanford.edu/data/web-Google.html), then place `web-Google.txt` at:

```text
hw04-pagerank/data/web-Google.txt
```

## Run

```bash
python pagerank.py
```

The recorded full-data run processed 875,713 nodes and 5,105,039 edges. See [analysis.md](analysis.md) for the results and complexity discussion.
