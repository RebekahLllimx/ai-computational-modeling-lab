# HW02: Network homophily

This assignment measures gender homophily in Facebook ego-networks and simulates network evolution through friendship and group-affiliation closure.

The comparison reports observed same-type edge rates against a baseline implied by the node-type distribution. Across the ten analyzed ego-networks, every estimated homophily index is positive, although effect sizes vary.

## Data

Download `facebook.tar.gz` from the [SNAP Facebook Social Circles page](https://snap.stanford.edu/data/ego-Facebook.html), extract it, and place the dataset at:

```text
hw02-network-homophily/data/facebook/
```

## Run

```bash
python ego0_homophily.py
python compare_ego_networks.py
python network_evolution.py
```

See [results/analysis.md](results/analysis.md) for the recorded comparison and evolution trace.
