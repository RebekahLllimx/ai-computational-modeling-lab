"""Measure gender-feature homophily in SNAP Facebook ego networks.

The two anonymized gender features are treated as categories; their numeric
identifiers do not establish which category is male or female. The analysis
adds an ego-to-alter edge for each node in the feature file, matching the
recorded course analysis.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATA = Path(__file__).resolve().parent / "data" / "facebook"


@dataclass(frozen=True)
class HomophilyResult:
    ego_id: int
    known_nodes: int
    valid_edges: int
    observed: float
    expected: float

    @property
    def excess(self) -> float:
        return self.observed - self.expected


def gender_feature_indices(path: Path) -> tuple[int, int]:
    """Find the two anonymized gender dimensions for this ego network."""
    indices = sorted(
        int(parts[0])
        for line in path.read_text(encoding="utf-8").splitlines()
        if (parts := line.split()) and "gender" in line.lower()
    )
    if len(indices) != 2:
        raise ValueError(f"Expected two gender feature dimensions in {path}")
    return indices[0], indices[1]


def read_features(data_dir: Path, ego_id: int) -> dict[int, tuple[int, ...]]:
    """Read alter features and the ego vector, which has no leading node ID."""
    features = {}
    for line in (data_dir / f"{ego_id}.feat").read_text(encoding="utf-8").splitlines():
        values = tuple(map(int, line.split()))
        if values:
            features[values[0]] = values[1:]
    features[ego_id] = tuple(
        map(int, (data_dir / f"{ego_id}.egofeat").read_text(encoding="utf-8").split())
    )
    return features


def network_edges(data_dir: Path, ego_id: int, nodes: set[int]) -> set[tuple[int, int]]:
    """Combine alter-to-alter edges with the ego-to-listed-alter edges."""
    edges = {tuple(sorted((ego_id, node))) for node in nodes if node != ego_id}
    for line in (data_dir / f"{ego_id}.edges").read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        u, v = map(int, parts[:2])
        if u in nodes and v in nodes and u != v:
            edges.add(tuple(sorted((u, v))))
    return edges


def analyze_ego_network(data_dir: Path, ego_id: int) -> HomophilyResult:
    indices = gender_feature_indices(data_dir / f"{ego_id}.featnames")
    features = read_features(data_dir, ego_id)
    categories = {}
    for node, vector in features.items():
        if len(vector) <= max(indices):
            raise ValueError(f"Feature vector for node {node} is too short")
        category = tuple(vector[index] for index in indices)
        if any(category):
            categories[node] = category

    if not categories:
        raise ValueError(f"No known gender features for ego network {ego_id}")

    edges = network_edges(data_dir, ego_id, set(features))
    valid = [(u, v) for u, v in edges if u in categories and v in categories]
    if not valid:
        raise ValueError(f"No edges with known gender features for ego network {ego_id}")
    observed = sum(categories[u] == categories[v] for u, v in valid) / len(valid)
    counts = Counter(categories.values())
    expected = sum((count / len(categories)) ** 2 for count in counts.values())
    return HomophilyResult(ego_id, len(categories), len(valid), observed, expected)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--ego", type=int, help="analyze one ego; default: all available egos")
    args = parser.parse_args(argv)
    if args.ego is None:
        ego_ids = sorted(int(path.stem) for path in args.data_dir.glob("*.egofeat"))
        if not ego_ids:
            parser.error(f"No .egofeat files found in {args.data_dir}")
    else:
        ego_ids = [args.ego]
    print(f"{'Ego':>5} {'Known nodes':>12} {'Valid edges':>12} {'Observed':>10} {'Expected':>10} {'Excess':>10}")
    for ego_id in ego_ids:
        result = analyze_ego_network(args.data_dir, ego_id)
        print(f"{result.ego_id:>5} {result.known_nodes:>12} {result.valid_edges:>12} "
              f"{result.observed:>10.4f} {result.expected:>10.4f} {result.excess:>10.4f}")


if __name__ == "__main__":
    main()
