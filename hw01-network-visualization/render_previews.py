"""Create static, reproducible previews of the two network visualizations."""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"

# English names for the twelve highest-weight nodes in the source table.
NAMES = {
    "宝玉": "Baoyu", "贾母": "Grandmother Jia", "凤姐": "Wang Xifeng",
    "袭人": "Xiren", "黛玉": "Daiyu", "宝钗": "Baochai",
    "贾琏": "Jia Lian", "平儿": "Ping'er", "贾政": "Jia Zheng",
    "鸳鸯": "Yuanyang", "紫鹃": "Zijuan", "李纨": "Li Wan",
}


def facebook_preview():
    alters = nx.read_edgelist(DATA / "0.edges", nodetype=int)
    ego = 0
    if ego in alters:
        raise ValueError("The ego ID is already present in the alter edge list")
    graph = alters.copy()
    graph.add_edges_from((ego, node) for node in alters)
    layout = nx.spring_layout(graph, seed=42, iterations=160, k=0.15)

    fig, ax = plt.subplots(figsize=(9, 8), constrained_layout=True)
    nx.draw_networkx_edges(graph, layout, edgelist=list(alters.edges), ax=ax,
                           edge_color="#aab5be", width=0.4, alpha=0.32)
    nx.draw_networkx_edges(graph, layout, edgelist=list(graph.edges(ego)), ax=ax,
                           edge_color="#83b4d1", width=0.5, alpha=0.32)
    nx.draw_networkx_nodes(graph, layout, nodelist=list(alters), ax=ax,
                           node_color="#3977a3", node_size=12)
    nx.draw_networkx_nodes(graph, layout, nodelist=[ego], ax=ax,
                           node_color="#d15d40", node_size=100)
    ax.set_title("Facebook ego network: ego 0", fontsize=15)
    ax.legend(handles=[
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#d15d40",
               markersize=8, label="Ego"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#3977a3",
               markersize=6, label="Alter"),
        Line2D([0], [0], color="#83b4d1", lw=1.2, label="Ego-alter link"),
        Line2D([0], [0], color="#aab5be", lw=1.2, label="Alter-alter link"),
    ], loc="upper right", frameon=False)
    ax.text(0.02, 0.02, f"{graph.number_of_nodes():,} nodes | {graph.number_of_edges():,} edges",
            transform=ax.transAxes, fontsize=9, color="#4d5961")
    ax.axis("off")
    fig.savefig(RESULTS / "facebook_ego_preview.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def character_preview():
    with (DATA / "NameNode.csv").open(newline="", encoding="utf-8") as source:
        records = sorted(csv.DictReader(source), key=lambda r: float(r["Weight"]), reverse=True)
    selected = records[:12]
    graph = nx.Graph()
    for row in selected:
        graph.add_node(row["ID"], weight=float(row["Weight"]))
    with (DATA / "relationship.csv").open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            if row["Source"] in graph and row["Target"] in graph:
                graph.add_edge(row["Source"], row["Target"], weight=float(row["Weight"]))

    layout = nx.circular_layout(graph)
    node_weights = np.array([graph.nodes[node]["weight"] for node in graph])
    node_sizes = 150 + 1200 * node_weights / node_weights.max()
    edge_weights = np.array([data["weight"] for _, _, data in graph.edges(data=True)])
    edge_widths = 0.3 + 3 * np.log1p(edge_weights) / np.log1p(edge_weights.max())
    fig, ax = plt.subplots(figsize=(10, 9), constrained_layout=True)
    nx.draw_networkx_edges(graph, layout, ax=ax, width=edge_widths,
                           edge_color="#7995a9", alpha=0.30)
    nx.draw_networkx_nodes(graph, layout, ax=ax, node_size=node_sizes,
                           node_color="#3977a3", edgecolors="white", linewidths=1)
    for node, position in layout.items():
        x, y = position * 1.16
        align = "left" if x > 0.1 else "right" if x < -0.1 else "center"
        ax.text(x, y, NAMES[node], ha=align, va="center", fontsize=10)
    ax.set_title("Character relationships in Dream of the Red Chamber", fontsize=15)
    ax.text(0.5, 0.02, "Twelve highest-weight characters; node size and line width reflect source weights.",
            transform=ax.transAxes, ha="center", fontsize=9, color="#4d5961")
    ax.set(xlim=(-1.5, 1.5), ylim=(-1.35, 1.35), aspect="equal")
    ax.axis("off")
    fig.savefig(RESULTS / "character_network_preview.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    RESULTS.mkdir(exist_ok=True)
    facebook_preview()
    character_preview()


if __name__ == "__main__":
    main()
