import networkx as nx
from pyvis.network import Network
from pathlib import Path

# -------------------------- 1. 配置文件路径 --------------------------
BASE_DIR = Path(__file__).resolve().parent
edges_file_path = BASE_DIR / "data" / "0.edges"
html_output_path = BASE_DIR / "results" / "facebook_network.html"

# -------------------------- 2. 读取edges文件并构建网络图 --------------------------
# 创建无向图
G = nx.Graph()

# 添加ego节点（ID=0）
G.add_node(0, label="Ego (ID=0)", size=20, color="#FF0000")  # 红色、更大的节点突出ego

# 读取edges文件并添加边
try:
    with open(edges_file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            # 清理每行内容（去除空格、换行符）
            line = line.strip()
            if not line:  # 跳过空行
                continue
            # 分割两个节点ID
            parts = line.split()
            if len(parts) != 2:
                print(f"警告：第{line_num}行格式错误，跳过（内容：{line}）")
                continue
            # 转换为整数节点ID
            try:
                node1 = int(parts[0])
                node2 = int(parts[1])
            except ValueError:
                print(f"警告：第{line_num}行不是数字，跳过（内容：{line}）")
                continue

            # 添加alter之间的边
            G.add_edge(node1, node2, color="#999999", width=1)
            # 添加每个alter与ego节点（0）的边
            G.add_edge(0, node1, color="#0066CC", width=2)
            G.add_edge(0, node2, color="#0066CC", width=2)

            # 设置alter节点的样式（蓝色、较小的节点）
            G.nodes[node1]["label"] = f"Alter ({node1})"
            G.nodes[node1]["size"] = 10
            G.nodes[node1]["color"] = "#0066CC"
            G.nodes[node2]["label"] = f"Alter ({node2})"
            G.nodes[node2]["size"] = 10
            G.nodes[node2]["color"] = "#0066CC"

    print(f"成功读取边文件，共加载 {G.number_of_nodes()} 个节点，{G.number_of_edges()} 条边")

except FileNotFoundError:
    print(f"错误：未找到文件 {edges_file_path}，请检查路径是否正确")
    exit(1)
except Exception as e:
    print(f"读取文件时出错：{str(e)}")
    exit(1)

# -------------------------- 3. 使用pyvis可视化并导出HTML --------------------------
# 初始化pyvis网络（设置宽度、高度，开启物理引擎）
net = Network(
    height="800px",
    width="100%",
    bgcolor="#ffffff",
    font_color="#000000",
    directed=False,
    notebook=False,
    cdn_resources="in_line"
)

# 将networkx的图导入pyvis
net.from_nx(G)

# 配置物理引擎（优化节点布局）
# 第一版代码的set_options部分，新增randomSeed和足够的迭代次数
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

# 保存可视化结果为HTML文件
net.write_html(str(html_output_path))
print(f"HTML可视化文件已保存至：{html_output_path}")
