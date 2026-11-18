import networkx as nx
import csv
from pyvis.network import Network
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
node_file = BASE_DIR / "data" / "NameNode.csv"
edge_file = BASE_DIR / "data" / "relationship.csv"
output_path = BASE_DIR / "results" / "honglou_weight.html"

honglou = nx.Graph()

csvfile = open(node_file, "r", encoding="utf-8")
reader = csv.DictReader(csvfile)
MIN_NODE_SIZE = 4
MAX_NODE_SIZE = 15
# Scale node weights into a readable size range.
node_weights = []
for row in reader:
    node_weights.append(float(row["Weight"]))
csvfile.close()
min_w = min(node_weights)
max_w = max(node_weights)
def normalize_node_weight(w):
    if max_w == min_w:
        return MIN_NODE_SIZE
    return MIN_NODE_SIZE + (float(w) - min_w) * (MAX_NODE_SIZE - MIN_NODE_SIZE) / (max_w - min_w)

csvfile = open(node_file, "r", encoding="utf-8")
reader = csv.DictReader(csvfile)
for row in reader:
    node_size = normalize_node_weight(row["Weight"])
    honglou.add_node(
        row["ID"],
        label=row["Label"],
        size=node_size,
        weight=float(row["Weight"]),
        title=f"{row['Label']} (Weight: {row['Weight']})"  # Show the node weight on hover.
    )
csvfile.close()

csvfile = open(edge_file, "r", encoding="utf-8")
reader = csv.DictReader(csvfile)
MIN_EDGE_WIDTH = 0.3
MAX_EDGE_WIDTH = 3
# Scale edge weights separately from node weights.
edge_weights = []
for row in reader:
    edge_weights.append(float(row["Weight"]))
csvfile.close()
min_ew = min(edge_weights)
max_ew = max(edge_weights)
def normalize_edge_weight(w):
    if max_ew == min_ew:
        return MIN_EDGE_WIDTH
    return MIN_EDGE_WIDTH + (float(w) - min_ew) * (MAX_EDGE_WIDTH - MIN_EDGE_WIDTH) / (max_ew - min_ew)

csvfile = open(edge_file, "r", encoding="utf-8")
reader = csv.DictReader(csvfile)
for row in reader:
    edge_width = normalize_edge_weight(row["Weight"])
    honglou.add_edge(
        row["Source"],
        row["Target"],
        value=edge_width,
        weight=float(row["Weight"]),
        title=f"Relationship weight: {row['Weight']}"  # Show the edge weight on hover.
    )
csvfile.close()

nt = Network(
    height="1000px",
    width="100%",
    bgcolor="#1a1a1a",
    font_color="#ffffff",
    notebook=False,
    directed=False,
    cdn_resources="in_line"
)

nt.from_nx(honglou)

nt.set_options('{ "physics": { "enabled": true, "stabilization": { "enabled": true, "iterations": 1000, "fit": true }, "forceAtlas2Based": { "gravitationalConstant": -100, "centralGravity": 0.01, "springLength": 150, "springConstant": 0.04, "damping": 0.9, "avoidOverlap": 0.8 }, "minVelocity": 0.01, "maxVelocity": 20 }, "nodes": { "shape": "dot", "font": {"size": 10}, "borderWidth": 1, "shadow": true }, "edges": { "color": {"color": "#888888", "inherit": false}, "smooth": {"type": "curvedCW"} }, "interaction": {"hover": true} }')

# Stop physics when the layout has stabilized.
custom_js = """
<script>
window.onload = function() {
  network.on("stabilizationIterationsDone", function() {
    network.setOptions({physics: {enabled: false}});
  });
};
</script>
"""

nt.write_html(str(output_path))
with open(output_path, 'r', encoding='utf-8') as f:
    html_content = f.read()
html_content = html_content.replace('</body>', custom_js + '</body>')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Weighted network visualization saved to {output_path}")
print(f"Node sizes: {MIN_NODE_SIZE}-{MAX_NODE_SIZE}px; larger nodes have higher weights.")
print(f"Edge widths: {MIN_EDGE_WIDTH}-{MAX_EDGE_WIDTH}px; wider edges have higher weights.")
print("The layout freezes after stabilization; hover over nodes and edges to inspect weights.")
