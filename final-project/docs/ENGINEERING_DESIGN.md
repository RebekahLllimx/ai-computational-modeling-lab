# Engineering design: Leviathan spatial game

## 1. Problem and requirements

### Problem

The experiment asks when a centralized penalty can preserve cooperation in a spatial Prisoner's Dilemma. It converts a philosophical claim into an explicit computational model whose assumptions, state transitions, and measurements can be inspected.

### Intended users

- Researchers or students reproducing the parameter sweep.
- Readers examining the mapping from a political-philosophy claim to a formal model.
- Developers extending the model with alternative update rules, institutions, or network structures.

### Functional requirements

- Initialize a seeded square lattice of cooperators and defectors.
- Evolve strategies synchronously under periodic Moore-neighborhood interactions.
- Introduce a configurable penalty at a specified time.
- Track cooperation, periodic cooperator clusters, the largest cluster, and C-D interface density.
- Run paired baseline and intervention conditions from identical initial states.
- Serialize numeric results and snapshots without pickle-dependent object arrays.
- Generate the report figures from saved experiment outputs.

### Non-functional requirements

- Deterministic replay for a fixed seed and configuration.
- Transparent, vectorized transition logic rather than a hidden learned policy.
- Explicit intervention timing and consistent periodic topology.
- Tests for boundary behavior, reproducibility, parameter validation, and paired histories.
- A quick smoke run that completes without the full parameter sweep.

## 2. System architecture

```text
Experiment configuration
        |
        v
run_experiments.py -----> HobbesCA (ca_model.py)
        |                        |
        |                        +--> synchronous state transition
        |                        +--> periodic cluster metrics
        v
numeric NPZ + JSON summaries + snapshot NPZ
        |
        v
visualization.py -----> figures
```

### Modules

- `ca_model.py` owns the simulation state, transition rule, metric definitions, and cross-run aggregation.
- `run_experiments.py` owns the baseline/intervention matrix, seed pairing, snapshots, and result persistence.
- `visualization.py` reads persisted outputs and generates all analytical figures.
- `quick_demo.py` exercises the model on a small grid for environment and interface checks.
- `tests/test_ca_model.py` verifies the core model independently of the long experiment.

### Data flow

1. The runner constructs a model from a parameter combination and seed.
2. Each transition computes local cooperation counts, payoffs, any active penalty, and the best neighboring strategy.
3. The model emits time-indexed metrics; the runner aggregates repetitions.
4. The runner writes numeric arrays and metadata to `src/outputs/`.
5. The visualization module reconstructs numeric parameter keys and renders figures.

### Technology choices

- NumPy provides array state, rolling neighborhoods, and vectorized strategy selection.
- SciPy convolution counts periodic neighbors; SciPy labeling identifies planar cluster fragments before seam components are merged.
- Matplotlib and Seaborn render static research figures.
- The standard `unittest` runner keeps validation available without adding a test-only dependency.

## 3. Interfaces and data design

### Model interface

From `final-project/src/`:

```python
from ca_model import HobbesCA

model = HobbesCA(
    grid_size=100,
    b=1.6,
    p=0.3,
    leviathan_time=500,
    seed=42,
)
metrics = model.run(steps=1000)
snapshot = model.get_snapshot()
```

`step()` advances one synchronous transition and returns the model's current grid array. Use `get_snapshot()` when an independent copy is required. `time` is the index of the current state. `run(steps)` records metrics after each transition, so a fresh model returns time indices `1` through `steps`, not the initial state. If `leviathan_time=500`, the state at `t=500` is the last shared pre-intervention state and the penalty affects the next transition.

### State and contracts

- Grid shape: `(grid_size, grid_size)`.
- Cell encoding: `1` for cooperator and `0` for defector.
- Boundary condition: periodic in both dimensions.
- Neighborhood: eight-cell Moore neighborhood.
- Payoffs: cooperator `n_coop`; defector `b * n_coop`, less `p` when the intervention is active.
- Update rule: imitate the highest-payoff strategy among self and eight neighbors. Self wins a tie only if its payoff equals the maximum; ties between higher-payoff neighbors use the fixed array order in `step()`.

### Persisted outputs

- `summary.json`: mean and standard deviation (`ddof=0`) across repetitions by condition and parameter combination.
- `raw_metrics.npz`: one numeric array per condition, parameter combination, repetition, and metric; for example, `A_b1.6_rep0_f_c` and `B_b1.6_p0.1_rep0_f_c`.
- `snapshots.npz`: flattened keys for condition, parameter values, and time.
- `metadata.json`: experiment dimensions, parameter lists, intervention timing, snapshot times, and a run timestamp. Seeds are configured in `run_experiments.py`: `BASE_SEED=42`, with repetition `i` using `42+i`; they are not currently copied into this JSON file.

Load the NPZ files with `np.load(path, allow_pickle=False)`. The reference sweep's metric series have 1,000 samples indexed by states `1..1000`; snapshots also include state zero. Both the runner and figure generator overwrite files in `src/outputs/`. The committed `figures/current_*.png` images are selected reference exports and are not replaced by those commands.

## 4. Implementation

### Core mechanism

The transition is vectorized across the grid. A wrapped convolution calculates cooperating neighbors. Payoffs are computed by strategy, then the intervention subtracts a constant penalty from defectors when active. Nine aligned payoff and strategy arrays represent self plus eight neighbors. `argmax` selects the best location and `take_along_axis` copies its strategy into the next state.

Periodic cluster measurement begins with 8-connected planar components. A union-find pass merges component labels that meet across the top/bottom and left/right seams, including diagonal seam contacts. This keeps the measurement topology consistent with the evolution topology.

### Error handling

The constructor rejects invalid grid sizes, temptation values, penalties, and intervention times. `run()` rejects negative step counts. Cross-run aggregation rejects series with inconsistent time axes instead of silently broadcasting or truncating them.

### State management

The model owns only the current grid, time, immutable parameters, and its seeded random generator. Intervention activity is derived from `time` rather than stored as a second mutable flag, avoiding synchronization errors after inspection or extension.

### Configuration and dependencies

The full experiment parameters are declared together at the top of `run_experiments.py`. Python dependencies are listed in the repository-level `requirements.txt`. Generated experiment arrays are excluded from version control and can be rebuilt from source.

## 5. Testing and validation

### Unit tests

- Opposite borders and wrapped corners form one periodic cluster.
- Separate interior clusters remain separate.
- Empty and full lattices produce correct metrics.
- Equal seeds reproduce both metric series and final state.
- Baseline and intervention runs remain identical through the intervention state.
- Invalid configurations fail explicitly.
- Aggregation requires a shared time axis.

### Integration checks

`quick_demo.py` runs both conditions on a 20 x 20 grid and prints final metrics. The full integration path is `run_experiments.py` followed by `visualization.py`; it regenerates serialized evidence and figures from a clean environment.

### Edge cases

The test suite covers zero cooperators, all cooperators, clusters split by periodic seams, invalid inputs, and paired histories. Long-run parameter sensitivity remains an experimental validation concern rather than a unit-test concern.

## 6. Deployment and operations

Run the experiment locally in the Python environment from the root README. The workflow uses no server or external API. Progress is printed per parameter combination with elapsed time and final cooperation.

An interrupted sweep must be rerun because there are no checkpoints. Copy any outputs that need to be retained before starting another sweep. Keep the source revision and `BASE_SEED` with archived results; metadata records the timestamp and parameter configuration but omits the seed and dependency versions.

## 7. Limitations and technical decisions

### Current limitations

- The institution is an exogenous payoff penalty rather than an endogenous collective choice.
- Agents use deterministic imitation and have no memory, beliefs, or heterogeneous preferences.
- The lattice is fixed and regular; social ties do not evolve.
- Five repetitions describe this model sweep but are not a substitute for broad uncertainty analysis.
- The runner uses a static configuration rather than a command-line or YAML experiment specification.

### Alternatives not selected

- Agent-based frameworks were unnecessary for a model whose update can be expressed transparently as array operations.
- A relational database would add operational complexity without improving bounded immutable result storage.
- Asynchronous or stochastic updates would answer a different modeling question and would break direct comparison with the archived study.
- Distributed execution was not justified by the reference workload.

### Next improvements

- Add a command-line configuration layer and resumable checkpoints.
- Record environment versions alongside experiment metadata.
- Add property-based tests for periodic connectivity.
- Compare deterministic, stochastic, and asynchronous update rules.
- Run a larger seed set and report confidence intervals for intervention effects.
- Model endogenous institution formation and institutional cost.
