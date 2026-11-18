# HW02: Network homophily

This assignment has two connected parts. The first reproduces the slide-deck
gender-homophily analysis for ego network 0 and applies the same comparison to
the other Facebook ego networks. The second implements a specified network
evolution exercise: starting from the supplied adjacency and club-affiliation
matrices, it applies the given friendship and club-joining rules until the
network converges.

The comparison reports observed same-type edge rates against a baseline implied by the node-type distribution. Across the ten analyzed ego-networks, every estimated homophily index is positive, although effect sizes vary.

`network_evolution.py` records the new edges and club memberships at each step,
draws the evolving network, and recalculates homophily for the four club-status
categories. It is part of the original assignment rather than a later
portfolio extension.

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
