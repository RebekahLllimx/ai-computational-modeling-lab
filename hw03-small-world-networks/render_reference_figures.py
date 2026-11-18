"""Render the recorded small-world results from the committed data extracts."""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"


def rows(filename):
    with (DATA / filename).open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def ordered_edge(a, b):
    return tuple(sorted((a, b)))


def plot_networks():
    # A 20 x 20 interior crop of the original 100 x 100 lattice.
    original = set()
    for x in range(20):
        for y in range(20):
            for dx, dy in ((1, -1), (1, 0), (1, 1), (0, 1)):
                neighbor = (x + dx, y + dy)
                if 0 <= neighbor[0] < 20 and 0 <= neighbor[1] < 20:
                    original.add(ordered_edge((x, y), neighbor))
    rewired = {
        ordered_edge((int(row["x1"]), int(row["y1"])),
                     (int(row["x2"]), int(row["y2"])))
        for row in rows("ws_reference_crop_edges.csv")
    }

    fig, axes = plt.subplots(1, 2, figsize=(12, 6), constrained_layout=True)
    for ax, edge_set, title in zip(axes, (original, rewired),
                                   ("Regular lattice", "After rewiring (p = 0.1)")):
        local_edges = edge_set & original
        added_edges = edge_set - original
        ax.add_collection(LineCollection(list(local_edges), colors="#9aa8b2", linewidths=0.45))
        if added_edges:
            ax.add_collection(LineCollection(list(added_edges), colors="#d76b32", linewidths=1.1))
        xx, yy = zip(*[(x, y) for x in range(20) for y in range(20)])
        ax.scatter(xx, yy, s=6, color="#286592", zorder=2)
        ax.set(xlim=(-1, 20), ylim=(-1, 20), aspect="equal", title=title)
        ax.axis("off")
    fig.suptitle("Watts-Strogatz network: 20 x 20 interior crop", fontsize=15)
    axes[1].legend(handles=[Line2D([0], [0], color="#d76b32", lw=1.5,
                                   label="New connection within crop")],
                   loc="lower center", frameon=False, fontsize=9)
    fig.text(0.5, 0.01, "Edges to nodes outside the crop are omitted.",
             ha="center", fontsize=9, color="#4d5961")
    fig.savefig(RESULTS / "ws_reference_networks.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_distance_distribution():
    data = rows("ws_reference_distance.csv")
    distance = [int(row["distance"]) for row in data]
    proportion = [float(row["reported_proportion"]) for row in data]
    fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
    ax.bar(distance, proportion, color="#3977a3", width=0.75)
    ax.set(title="Shortest-path distances in the recorded WS network",
           xlabel="Shortest-path length", ylabel="Reported proportion")
    ax.set_xticks(distance)
    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)
    fig.savefig(RESULTS / "ws_reference_distance.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_rank_distribution():
    data = rows("wsk_reference_rank_counts.csv")
    rank = np.array([int(row["distance_bin_rank"]) for row in data])
    counts = np.array([int(row["edge_incidences"]) for row in data])
    proportions = counts / counts.sum()
    slope, intercept = np.polyfit(np.log(rank), np.log(proportions), 1)
    xfit = np.geomspace(rank.min(), rank.max(), 150)
    fig, ax = plt.subplots(figsize=(8, 4.8), constrained_layout=True)
    ax.loglog(rank, proportions, "o", ms=3, color="#3977a3", alpha=0.75,
              label="Recorded distance-bin frequencies")
    ax.loglog(xfit, np.exp(intercept) * xfit ** slope, color="#c3553c",
              label=f"Log-log fit: slope {slope:.4f}")
    ax.set(title="Distance-bin frequencies in the recorded WSK network",
           xlabel="Ordinal rank of nonempty distance bin",
           ylabel="Share of link incidences")
    ax.grid(which="both", alpha=0.18)
    ax.legend(frameon=False)
    fig.savefig(RESULTS / "wsk_reference_rank.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    RESULTS.mkdir(exist_ok=True)
    plot_networks()
    plot_distance_distribution()
    plot_rank_distribution()


if __name__ == "__main__":
    main()
