import networkx as nx
from pyvis.network import Network
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
edges_file_path = BASE_DIR / "data" / "0.edges"
html_output_path = BASE_DIR / "results" / "facebook_network.html"

G = nx.Graph()

G.add_node(0, label="Ego (ID=0)", size=20, color="#FF0000")

try:
    with open(edges_file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 2:
                print(f"Warning: skipping malformed line {line_num}: {line}")
                continue
            try:
                node1 = int(parts[0])
                node2 = int(parts[1])
            except ValueError:
                print(f"Warning: skipping line {line_num} with non-integer node IDs: {line}")
                continue

            G.add_edge(node1, node2, color="#999999", width=1)
            # The edge list omits links to the ego; add them explicitly.
            G.add_edge(0, node1, color="#0066CC", width=2)
            G.add_edge(0, node2, color="#0066CC", width=2)

            G.nodes[node1]["label"] = f"Alter ({node1})"
            G.nodes[node1]["size"] = 10
            G.nodes[node1]["color"] = "#0066CC"
            G.nodes[node2]["label"] = f"Alter ({node2})"
            G.nodes[node2]["size"] = 10
            G.nodes[node2]["color"] = "#0066CC"

    print(f"Loaded {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

except FileNotFoundError:
    print(f"Edge list not found: {edges_file_path}")
    exit(1)
except Exception as e:
    print(f"Could not read the edge list: {e}")
    exit(1)

net = Network(
    height="800px",
    width="100%",
    bgcolor="#ffffff",
    font_color="#000000",
    directed=False,
    notebook=False,
    cdn_resources="in_line"
)

net.from_nx(G)

net.set_options("""
var options = {
  "physics": {
    "forceAtlas2Based": {
      "gravitationalConstant": -200,
      "centralGravity": 0.1,
      "springLength": 100,
      "springConstant": 0.08
    },
    "maxVelocity": 50,
    "solver": "forceAtlas2Based",
    "timestep": 0.35,
    "stabilization": {
      "iterations": 500
    }
  },
  "layout": {
    "randomSeed": 42
  }
}
""")

net.write_html(str(html_output_path))
print(f"Interactive graph saved to {html_output_path}")
