import networkx as nx
import csv
from pyvis.network import Network
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
node_file = BASE_DIR / "data" / "NameNode.csv"
edge_file = BASE_DIR / "data" / "relationship.csv"
output_path = BASE_DIR / "results" / "honglou_weight.html"

# 1. 构建NetworkX图（保留权重信息）
honglou = nx.Graph()

# 读入节点（带Weight，动态调整大小）
csvfile = open(node_file, "r", encoding="utf-8")
reader = csv.DictReader(csvfile)
# 节点大小参数（控制范围，避免过大/过小）
MIN_NODE_SIZE = 4
MAX_NODE_SIZE = 15
# 先获取所有节点权重，计算归一化范围
node_weights = []
for row in reader:
    node_weights.append(float(row["Weight"]))
csvfile.close()
# 归一化权重（映射到MIN-MAX_NODE_SIZE）
min_w = min(node_weights)
max_w = max(node_weights)
def normalize_node_weight(w):
    if max_w == min_w:
        return MIN_NODE_SIZE  # 权重相同则用最小尺寸
    return MIN_NODE_SIZE + (float(w) - min_w) * (MAX_NODE_SIZE - MIN_NODE_SIZE) / (max_w - min_w)

# 重新读取节点，添加带权重的节点
csvfile = open(node_file, "r", encoding="utf-8")
reader = csv.DictReader(csvfile)
for row in reader:
    node_size = normalize_node_weight(row["Weight"])
    honglou.add_node(
        row["ID"],
        label=row["Label"],
        size=node_size,  # 权重映射的节点大小
        weight=float(row["Weight"]),
        title=f"{row['Label']} (权重: {row['Weight']})"  # 悬浮提示权重
    )
csvfile.close()

# 读入边（带Weight，动态调整粗细）
csvfile = open(edge_file, "r", encoding="utf-8")
reader = csv.DictReader(csvfile)
# 边粗细参数
MIN_EDGE_WIDTH = 0.3
MAX_EDGE_WIDTH = 3
# 先获取所有边权重，计算归一化范围
edge_weights = []
for row in reader:
    edge_weights.append(float(row["Weight"]))
csvfile.close()
# 归一化权重（映射到MIN-MAX_EDGE_WIDTH）
min_ew = min(edge_weights)
max_ew = max(edge_weights)
def normalize_edge_weight(w):
    if max_ew == min_ew:
        return MIN_EDGE_WIDTH
    return MIN_EDGE_WIDTH + (float(w) - min_ew) * (MAX_EDGE_WIDTH - MIN_EDGE_WIDTH) / (max_ew - min_ew)

# 重新读取边，添加带权重的边
csvfile = open(edge_file, "r", encoding="utf-8")
reader = csv.DictReader(csvfile)
for row in reader:
    edge_width = normalize_edge_weight(row["Weight"])
    honglou.add_edge(
        row["Source"],
        row["Target"],
        value=edge_width,  # 权重映射的边粗细
        weight=float(row["Weight"]),
        title=f"关系权重: {row['Weight']}"  # 悬浮提示权重
    )
csvfile.close()

# 2. 初始化pyvis网络（3D立体+深色背景）
nt = Network(
    height="1000px",
    width="100%",
    bgcolor="#1a1a1a",
    font_color="#ffffff",
    notebook=False,
    directed=False,
    cdn_resources="in_line"
)

# 3. 从NetworkX导入图（保留权重属性）
nt.from_nx(honglou)

# 4. 核心配置：自然收敛物理引擎（纯JSON，无注释）
nt.set_options('{ "physics": { "enabled": true, "stabilization": { "enabled": true, "iterations": 1000, "fit": true }, "forceAtlas2Based": { "gravitationalConstant": -100, "centralGravity": 0.01, "springLength": 150, "springConstant": 0.04, "damping": 0.9, "avoidOverlap": 0.8 }, "minVelocity": 0.01, "maxVelocity": 20 }, "nodes": { "shape": "dot", "font": {"size": 10}, "borderWidth": 1, "shadow": true }, "edges": { "color": {"color": "#888888", "inherit": false}, "smooth": {"type": "curvedCW"} }, "interaction": {"hover": true} }')

# 5. 嵌入无注释JS：布局稳定后自动冻结
custom_js = """
<script>
window.onload = function() {
  network.on("stabilizationIterationsDone", function() {
    network.setOptions({physics: {enabled: false}});
  });
};
</script>
"""

# 6. 生成HTML并插入冻结逻辑
nt.write_html(str(output_path))
with open(output_path, 'r', encoding='utf-8') as f:
    html_content = f.read()
html_content = html_content.replace('</body>', custom_js + '</body>')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ 权重版可视化完成！文件路径：{output_path}")
print(f"📌 节点大小范围：{MIN_NODE_SIZE}-{MAX_NODE_SIZE}px（权重越高越大）")
print(f"📌 边粗细范围：{MIN_EDGE_WIDTH}-{MAX_EDGE_WIDTH}px（权重越高越粗）")
print("💡 打开网页后节点自然收敛，稳定后自动冻结，可悬浮查看权重！")
