import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def read_graph(file_path, max_lines=None):
    """Read the edge list into source, destination, and degree arrays."""
    nodes = set()
    with open(file_path, 'r') as f:
        lines_read = 0
        for line in f:
            if line.startswith('#'):
                continue
            if max_lines is not None and lines_read >= max_lines:
                break
            parts = line.strip().split()
            if len(parts) == 2:
                from_node, to_node = int(parts[0]), int(parts[1])
                nodes.add(from_node)
                nodes.add(to_node)
                lines_read += 1

    # Map arbitrary node IDs to contiguous array indices.
    nodes = sorted(nodes)
    node_to_index = {node: i for i, node in enumerate(nodes)}
    n = len(nodes)

    from_indices = []
    to_indices = []
    out_degrees = np.zeros(n, dtype=int)
    in_degrees = np.zeros(n, dtype=int)

    with open(file_path, 'r') as f:
        lines_read = 0
        for line in f:
            if line.startswith('#'):
                continue
            if max_lines is not None and lines_read >= max_lines:
                break
            parts = line.strip().split()
            if len(parts) == 2:
                from_node, to_node = int(parts[0]), int(parts[1])
                if from_node in node_to_index and to_node in node_to_index:
                    from_idx = node_to_index[from_node]
                    to_idx = node_to_index[to_node]
                    from_indices.append(from_idx)
                    to_indices.append(to_idx)
                    out_degrees[from_idx] += 1
                    in_degrees[to_idx] += 1
                lines_read += 1

    from_indices = np.array(from_indices, dtype=int)
    to_indices = np.array(to_indices, dtype=int)

    return from_indices, to_indices, out_degrees, in_degrees, nodes, node_to_index

def pagerank(from_indices, to_indices, out_degrees, in_degrees, nodes, node_to_index, s=0.85, max_iterations=100, tolerance=1e-6):
    """Compute PageRank with uniform teleportation and sink redistribution."""
    n = len(nodes)

    pr = np.ones(n, dtype=np.float64) / n

    sink_indices = np.where(out_degrees == 0)[0]
    num_sinks = len(sink_indices)

    weights = 1.0 / out_degrees[from_indices]
    weights[out_degrees[from_indices] == 0] = 0

    for i in range(max_iterations):
        old_pr = pr.copy()

        sink_pr = np.sum(pr[sink_indices]) if num_sinks > 0 else 0

        new_pr = np.zeros(n, dtype=np.float64)

        edge_contributions = s * pr[from_indices] * weights
        # Accumulate contributions from all edges sharing a destination.
        np.add.at(new_pr, to_indices, edge_contributions)

        # Redistribute sink mass, then add uniform teleportation.
        new_pr += s * (sink_pr / n)
        new_pr += (1 - s) / n

        pr = new_pr

        if np.linalg.norm(pr - old_pr) < tolerance:
            break

    result = {node: pr[node_to_index[node]] for node in nodes}
    return result, in_degrees

def visualize_in_degree_vs_pagerank(in_degrees, pr_values, nodes, node_to_index):
    """Plot PageRank against in-degree on logarithmic axes."""
    in_degree_list = []
    pr_list = []

    for node in nodes:
        idx = node_to_index[node]
        in_degree_list.append(in_degrees[idx])
        pr_list.append(pr_values[node])

    plt.figure(figsize=(12, 8))
    plt.scatter(in_degree_list, pr_list, alpha=0.5, s=10)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('In-Degree (log scale)')
    plt.ylabel('PageRank (log scale)')
    plt.title('Relationship between In-Degree and PageRank')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    output_path = BASE_DIR / 'results' / 'in_degree_vs_pagerank.png'
    output_path.parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Visualization saved as '{output_path}'")

    plt.show()

if __name__ == "__main__":
    file_path = BASE_DIR / "data" / "web-Google.txt"
    from_indices, to_indices, out_degrees, in_degrees, nodes, node_to_index = read_graph(file_path)
    print(f"Total nodes: {len(nodes)}")
    print(f"Total edges: {len(from_indices)}")

    pr_values, in_degrees = pagerank(from_indices, to_indices, out_degrees, in_degrees, nodes, node_to_index, s=0.85)

    print("Top 10 PageRank values:")
    sorted_pr = sorted(pr_values.items(), key=lambda x: x[1], reverse=True)[:10]
    for node, pr in sorted_pr:
        print(f"Node {node}: {pr:.6f}")

    visualize_in_degree_vs_pagerank(in_degrees, pr_values, nodes, node_to_index)
