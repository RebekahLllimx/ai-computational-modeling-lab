# AI & Computational Modeling Lab

Computational studies of social networks, ranking, and cooperation. The projects build and visualize graphs, implement ranking algorithms, and compare how local interaction rules change collective outcomes. Each includes its methods and instructions for running the code.

Developed for *Artificial Intelligence and Computational Thinking* (Spring 2026).

## Projects

| Project | Question and approach |
| --- | --- |
| [Network visualization](hw01-network-visualization/) | Build a weighted character network and explore a Facebook ego network with NetworkX and PyVis. |
| [Network homophily and evolution](hw02-network-homophily/) | Compare gender-feature homophily across ten Facebook ego networks; simulate how shared friends and clubs change a social network over time. |
| [Small-world networks](hw03-small-world-networks/) | Study distance and degree patterns in Watts-Strogatz and Kleinberg-style networks. |
| [PageRank](hw04-pagerank/) | Implement iterative PageRank and inspect the Web-Google graph. |
| [Game theory](hw05-game-theory/) | Work through two teaching cases with payoff matrices and Nash equilibria. |
| [Leviathan: punishment and cooperation](final-project/) | Use a spatial evolutionary game to test when centralized punishment sustains cooperation. |

## Featured experiment

The [final project](final-project/README.md) compares a spatial Prisoner's Dilemma with and without punishment of defectors. In the reference experiment, cooperation at `b = 1.6` averaged about 42% without the intervention and 73% with a penalty of `p = 0.1`. At `b >= 1.8`, the intervention did not restore cooperation after extinction. These outcomes describe the simulated model and parameter sweep.

![Comparison of the two model conditions](final-project/figures/current_ab_comparison.png)

The simulation and its cluster measurements use periodic eight-neighbor connectivity. The [technical report](final-project/report/technical_report.md) explains the experiment and its results.

## Run a small check

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s final-project/tests -v
python final-project/src/quick_demo.py
```

The quick demo uses a 20 x 20 grid for 20 steps. It checks the workflow; it does not reproduce the full study. For the 100 x 100, 1,000-step sweep and figure generation, follow the [final-project run guide](final-project/README.md). Other assignments have setup and data instructions in their own README files.

Dataset-independent regression checks for the network assignments can also run from the repository root:

```bash
python -m unittest discover -s hw02-network-homophily/tests -v
python -m unittest discover -s hw03-small-world-networks/tests -v
```

## Repository notes

- Large public datasets are downloaded from their original providers; they are not committed here.
- Randomized experiments use explicit seeds where supported. Saved figures are reference outputs, and source scripts are included for regeneration.
- Original code is available under the [MIT License](LICENSE). External data and research keep their own terms; see [third-party notices](THIRD_PARTY_NOTICES.md).
- The game-theory cases use teaching assumptions and subjective utilities. They are not legal advice or forecasts.
