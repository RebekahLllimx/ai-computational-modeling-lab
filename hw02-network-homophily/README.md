# HW02: Network homophily

This assignment has two connected parts. The required analysis measures gender
homophily in Facebook ego-networks. The accompanying slide deck also posed an
open reflection question about how the network might evolve; the
`network_evolution.py` extension answers it by simulating friendship and
group-affiliation closure over successive steps.

The comparison reports observed same-type edge rates against a baseline implied by the node-type distribution. Across the ten analyzed ego-networks, every estimated homophily index is positive, although effect sizes vary.

The evolution component is therefore part of the submitted intellectual work,
not a later portfolio feature. It turns the slide question into an explicit
update process and records how the homophily measures change after each step.

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
