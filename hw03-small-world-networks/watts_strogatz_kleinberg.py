import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import random
from collections import defaultdict
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent / "results" / "runs" / "wsk"


class WSKNetwork:
    def __init__(self, n, k, alpha):
        """
        Initialize a grid with local and distance-weighted links.
        n: lattice width and height
        k: number of local neighbors per node
        alpha: distance exponent
        """
        self.n = n
        self.k = k
        self.alpha = alpha
        self.N = n * n
        self.G = nx.Graph()
        self._build_network()

    def _node_to_pos(self, node):
        """Convert a node ID to grid coordinates."""
        return (node // self.n, node % self.n)

    def _pos_to_node(self, x, y):
        """Convert grid coordinates to a node ID."""
        return x * self.n + y

    def _manhattan_distance(self, pos1, pos2):
        """Return Manhattan distance without wrapping."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def _build_network(self):
        """Build the local lattice and sample one long-range target per node."""
        for i in range(self.N):
            self.G.add_node(i)

        # Wrap local neighbors at the grid boundary.
        for node in range(self.N):
            x, y = self._node_to_pos(node)
            neighbors = []
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dx, dy in directions:
                for d in range(1, self.k//4 + 1):
                    nx = (x + dx * d) % self.n
                    ny = (y + dy * d) % self.n
                    neighbor_node = self._pos_to_node(nx, ny)
                    if neighbor_node != node:
                        neighbors.append(neighbor_node)
            for neighbor in neighbors[:self.k]:
                self.G.add_edge(node, neighbor)

        for node in range(self.N):
            x, y = self._node_to_pos(node)
            distances = {}
            probabilities = {}
            total_prob = 0

            for other_node in range(self.N):
                if other_node == node:
                    continue
                ox, oy = self._node_to_pos(other_node)
                r = self._manhattan_distance((x, y), (ox, oy))
                if r == 0:
                    continue
                prob = 1.0 / (r ** self.alpha)
                distances[other_node] = r
                probabilities[other_node] = prob
                total_prob += prob

            for other_node in probabilities:
                probabilities[other_node] /= total_prob

            # Sample a target in proportion to distance raised to -alpha.
            if probabilities:
                selected_node = random.choices(
                    list(probabilities.keys()),
                    weights=list(probabilities.values()),
                    k=1
                )[0]
                self.G.add_edge(node, selected_node)

    def get_distance_distribution(self):
        """Sample shortest-path lengths between distinct nodes."""
        sample_size = min(1000, self.N // 10)
        distances = []

        for _ in range(sample_size):
            node1 = random.randint(0, self.N - 1)
            node2 = random.randint(0, self.N - 1)
            if node1 != node2:
                try:
                    distance = nx.shortest_path_length(self.G, node1, node2)
                    distances.append(distance)
                except nx.NetworkXNoPath:
                    pass

        return distances

    def get_rank_probability(self):
        """Return link-incidence proportions by ordinal distance-bin rank."""
        # Count each undirected edge once from each endpoint.
        distance_counts = defaultdict(int)
        total_pairs = 0

        for node in range(self.N):
            x, y = self._node_to_pos(node)
            for neighbor in self.G.neighbors(node):
                nx, ny = self._node_to_pos(neighbor)
                r = self._manhattan_distance((x, y), (nx, ny))
                if r > 0:
                    distance_counts[r] += 1
                    total_pairs += 1

        rank_prob = []
        sorted_distances = sorted(distance_counts.keys())
        for i, r in enumerate(sorted_distances):
            rank = i + 1
            prob = distance_counts[r] / total_pairs
            rank_prob.append((rank, prob))

        return rank_prob

    def visualize(self):
        """Draw the network at its grid coordinates."""
        pos = {node: self._node_to_pos(node) for node in self.G.nodes()}
        plt.figure(figsize=(10, 10))
        nx.draw(self.G, pos, node_size=10, alpha=0.5, with_labels=False)
        plt.title(f"WSK Network (n={self.n}, k={self.k}, alpha={self.alpha})")
        plt.savefig("network_visualization.png")
        plt.show()

def fit_power_law(rank_prob):
    """Fit a line to log rank and log proportion; return the negated slope."""
    ranks, probs = zip(*rank_prob)

    ranks = np.array(ranks)
    probs = np.array(probs)

    log_ranks = np.log(ranks)
    log_probs = np.log(probs)

    coefficients = np.polyfit(log_ranks, log_probs, 1)
    q = -coefficients[0]

    return q, coefficients

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Keep every generated artifact inside this assignment's results folder.
    import os
    os.chdir(OUTPUT_DIR)
    n = 100
    k = 4
    alpha = 2.0  # distance exponent

    print("Building WSK network...")
    network = WSKNetwork(n, k, alpha)
    print(f"Network built with {network.N} nodes and {network.G.number_of_edges()} edges")

    # Draw the network at its grid coordinates.
    network.visualize()

    # Sample shortest-path lengths between distinct nodes.
    print("Calculating distance distribution...")
    distances = network.get_distance_distribution()

    plt.figure(figsize=(10, 6))
    plt.hist(distances, bins=20, alpha=0.75)
    plt.title("Distance Distribution")
    plt.xlabel("Distance")
    plt.ylabel("Frequency")
    plt.xticks(range(11))
    plt.savefig("distance_distribution.png")
    plt.show()

    print("Calculating rank-probability relationship...")
    rank_prob = network.get_rank_probability()

    q, coefficients = fit_power_law(rank_prob)
    print(f"Estimated q value: {q:.4f}")

    ranks, probs = zip(*rank_prob)
    plt.figure(figsize=(10, 6))
    plt.loglog(ranks, probs, 'o', label='Data')

    fit_ranks = np.logspace(np.log10(min(ranks)), np.log10(max(ranks)), 100)
    fit_probs = np.exp(coefficients[1]) * (fit_ranks ** (-q))
    plt.loglog(fit_ranks, fit_probs, '-r', label=f'Log-log fit: slope {-q:.4f}')

    plt.title("Observed link frequencies by distance-bin rank")
    plt.xlabel("Ordinal rank of nonempty Manhattan-distance bin")
    plt.ylabel("Share of link incidences")
    plt.legend()
    plt.grid(True, which="both", ls="--")
    plt.savefig("rank_probability.png")
    plt.show()

    with open("result.md", "w") as f:
        f.write("# WSK Network Analysis\n")
        f.write(f"- Grid size: {n}x{n}\n")
        f.write(f"- Number of nodes: {network.N}\n")
        f.write(f"- Number of edges: {network.G.number_of_edges()}\n")
        f.write(f"- Clustering exponent alpha: {alpha}\n")
        f.write(f"- Fitted distance-bin slope: {-q:.4f}\n")

        f.write("\n## Network Visualization\n")
        f.write("![Network Visualization](network_visualization.png)\n")

        f.write("\n## Distance Distribution\n")
        f.write("![Distance Distribution](distance_distribution.png)\n")

        f.write("\n## Distance-bin frequencies\n")
        f.write("The rank is the ordinal index of a nonempty Manhattan-distance bin.\n\n")
        f.write("![Distance-bin frequencies](rank_probability.png)\n")

        f.write("\n## Rank-Probability Data\n")
        f.write("| Rank | Probability |\n")
        f.write("|------|-------------|\n")
        for rank, prob in rank_prob:
            f.write(f"| {rank} | {prob:.6f} |\n")

if __name__ == "__main__":
    main()
