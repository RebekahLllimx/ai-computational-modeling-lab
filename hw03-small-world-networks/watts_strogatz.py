import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import time
import plotly.graph_objects as go
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent / "results" / "runs" / "ws"

def create_lattice_graph(n):
    """Build an n x n periodic lattice with eight neighbors per node."""
    G = nx.Graph()
    for i in range(n):
        for j in range(n):
            node = i * n + j
            G.add_node(node)

    for i in range(n):
        for j in range(n):
            node = i * n + j
            directions = [(-1, -1), (-1, 0), (-1, 1),
                         (0, -1),          (0, 1),
                         (1, -1),  (1, 0), (1, 1)]
            for di, dj in directions:
                ni, nj = (i + di) % n, (j + dj) % n  # Wrap positions at the grid boundary.
                neighbor = ni * n + nj
                if neighbor > node:  # Add each undirected edge once.
                    G.add_edge(node, neighbor)
    return G

def watts_strogatz_rewire(G, p):
    """Rewire existing edges with probability p, preserving the edge count."""
    edges = list(G.edges())
    for u, v in edges:
        if np.random.random() < p:
            while True:
                w = np.random.choice(list(G.nodes()))
                if w != u and not G.has_edge(u, w):
                    break
            G.remove_edge(u, v)
            G.add_edge(u, w)
    return G

def calculate_distance_distribution(G):
    """Count shortest-path lengths between distinct nodes."""
    distance_counts = {}
    n = G.number_of_nodes()

    for node in G.nodes():
        distances = nx.shortest_path_length(G, node)
        for dist in distances.values():
            if dist == 0:  # Exclude self-pairs from the distinct-node denominator.
                continue
            if dist in distance_counts:
                distance_counts[dist] += 1
            else:
                distance_counts[dist] = 1

    total_pairs = n * (n - 1)  # Ordered pairs of distinct nodes.
    distance_probs = {k: v / total_pairs for k, v in distance_counts.items()}
    return distance_probs

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Keep every generated artifact inside this assignment's results folder.
    import os
    os.chdir(OUTPUT_DIR)
    n = 100
    p = 0.1

    print("Building a 100 x 100 lattice with eight neighbors per node...")
    start_time = time.time()
    G = create_lattice_graph(n)
    print(f"Lattice built in {time.time() - start_time:.2f} s")
    print(f"Initial edges: {G.number_of_edges()}")

    print("\nRewiring edges...")
    start_time = time.time()
    G = watts_strogatz_rewire(G, p)
    print(f"Rewiring finished in {time.time() - start_time:.2f} s")
    print(f"Edges after rewiring: {G.number_of_edges()}")

    print("\nCalculating shortest-path distances...")
    start_time = time.time()
    distance_probs = calculate_distance_distribution(G)
    print(f"Distance distribution calculated in {time.time() - start_time:.2f} s")

    print("\nDistance distribution:")
    for dist in sorted(distance_probs.keys()):
        print(f"Distance {dist}: proportion {distance_probs[dist]:.4f}")

    avg_path_length = nx.average_shortest_path_length(G)
    print(f"\nMean shortest-path length: {avg_path_length:.2f}")

    clustering_coefficient = nx.average_clustering(G)
    print(f"Mean clustering coefficient: {clustering_coefficient:.4f}")

    plt.figure(figsize=(10, 6))
    distances = sorted(distance_probs.keys())
    probabilities = [distance_probs[d] for d in distances]
    plt.bar(distances, probabilities)
    plt.xlabel('Shortest-path length')
    plt.ylabel('Reported proportion')
    plt.title('Watts-Strogatz shortest-path distribution')
    plt.xticks(range(11))
    plt.savefig('distance_distribution.png')
    print("\nSaved distance distribution to distance_distribution.png")

    print("\nDrawing the rewired lattice crop...")
    region_size = 20
    start_i, start_j = 40, 40

    sample_nodes = []
    for i in range(start_i, start_i + region_size):
        for j in range(start_j, start_j + region_size):
            node = i * n + j
            sample_nodes.append(node)

    subgraph = G.subgraph(sample_nodes)

    plt.figure(figsize=(15, 12))
    pos = {}
    for i in range(start_i, start_i + region_size):
        for j in range(start_j, start_j + region_size):
            node = i * n + j
            pos[node] = (j - start_j, start_i + region_size - 1 - i)

    nx.draw_networkx_nodes(subgraph, pos, node_size=100, alpha=0.8)
    nx.draw_networkx_edges(subgraph, pos, width=1.0, alpha=0.6)
    plt.title('Watts-Strogatz network (20 x 20 crop)')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('network_visualization.png', dpi=300)
    print("Saved the network crop to network_visualization.png")

    print("\nDrawing the regular lattice for comparison...")
    original_G = create_lattice_graph(region_size)
    original_pos = {}
    for i in range(region_size):
        for j in range(region_size):
            node = i * region_size + j
            original_pos[node] = (j, region_size - 1 - i)

    plt.figure(figsize=(15, 12))
    nx.draw_networkx_nodes(original_G, original_pos, node_size=100, alpha=0.8)
    nx.draw_networkx_edges(original_G, original_pos, width=1.0, alpha=0.6)
    plt.title('Original eight-neighbor lattice (20 x 20)')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('original_lattice.png', dpi=300)
    print("Saved the regular lattice to original_lattice.png")

    print("\nBuilding the interactive 100 x 100 network with Plotly...")
    plotly_pos = {}
    for i in range(n):
        for j in range(n):
            node = i * n + j
            plotly_pos[node] = (j, n - 1 - i)

    node_x = [plotly_pos[node][0] for node in G.nodes()]
    node_y = [plotly_pos[node][1] for node in G.nodes()]

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = plotly_pos[edge[0]]
        x1, y1 = plotly_pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color='blue',
            size=3,
            line_width=0
        )
    )

    layout = go.Layout(
        title=dict(
            text='Watts-Strogatz network (100 x 100)',
            font=dict(size=16)
        ),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    fig = go.Figure(data=[edge_trace, node_trace], layout=layout)

    fig.write_html('network_visualization_100x100.html')
    print("Saved the full network to network_visualization_100x100.html")

    return {
        'edges': G.number_of_edges(),
        'avg_path_length': avg_path_length,
        'clustering_coefficient': clustering_coefficient,
        'p': p,
        'distance_probs': distance_probs
    }

def write_result_to_md(results):
    """Write this run's measurements alongside its generated figures."""
    md_file = OUTPUT_DIR / "analysis.md"

    new_content = "# Watts-Strogatz Network Analysis\n"
    new_content += "- Grid size: 100x100\n"
    new_content += "- Number of nodes: 10000\n"
    new_content += f"- Number of edges: {results['edges']}\n"
    new_content += f"- Average path length: {results['avg_path_length']:.2f}\n"
    new_content += f"- Average clustering coefficient: {results['clustering_coefficient']:.4f}\n"
    new_content += f"- Rewiring probability: {results['p']}\n\n"

    new_content += "## Distance Distribution\n"
    new_content += "| Distance | Probability |\n"
    new_content += "|----------|-------------|\n"
    for dist in sorted(results['distance_probs'].keys()):
        if dist <= 20:
            new_content += f"| {dist} | {results['distance_probs'][dist]:.6f} |\n"
    new_content += "\n"

    new_content += "## Visualizations\n"
    new_content += "![Distance Distribution](distance_distribution.png)\n"
    new_content += "![Network Visualization (20x20)](network_visualization.png)\n"
    new_content += "![Original Lattice](original_lattice.png)\n"
    new_content += "[Interactive Network Visualization (100x100)](network_visualization_100x100.html)\n\n"

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"\nResults saved to {md_file}")

if __name__ == "__main__":
    results = main()
    write_result_to_md(results)
