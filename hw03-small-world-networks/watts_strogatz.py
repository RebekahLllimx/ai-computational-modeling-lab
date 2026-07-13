import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import time
import sys
import plotly.graph_objects as go
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent / "results"

# 构建100x100的8邻居网格图
def create_lattice_graph(n):
    """创建n x n的8邻居网格图"""
    G = nx.Graph()
    # 添加节点
    for i in range(n):
        for j in range(n):
            node = i * n + j
            G.add_node(node)

    # 添加8邻居边
    for i in range(n):
        for j in range(n):
            node = i * n + j
            # 8个方向的邻居
            directions = [(-1, -1), (-1, 0), (-1, 1),
                         (0, -1),          (0, 1),
                         (1, -1),  (1, 0), (1, 1)]
            for di, dj in directions:
                ni, nj = (i + di) % n, (j + dj) % n  # 周期性边界条件
                neighbor = ni * n + nj
                if neighbor > node:  # 避免重复添加边
                    G.add_edge(node, neighbor)
    return G

# Watts-Strogatz模型重连
def watts_strogatz_rewire(G, p):
    """按照Watts-Strogatz模型进行重连"""
    edges = list(G.edges())
    for u, v in edges:
        if np.random.random() < p:
            # 随机选择一个新的目标节点
            while True:
                w = np.random.choice(list(G.nodes()))
                if w != u and not G.has_edge(u, w):
                    break
            G.remove_edge(u, v)
            G.add_edge(u, w)
    return G

# 计算节点间距离分布
def calculate_distance_distribution(G):
    """计算所有节点对之间的距离分布"""
    distance_counts = {}
    n = G.number_of_nodes()

    # 对每个节点计算到其他节点的距离
    for node in G.nodes():
        distances = nx.shortest_path_length(G, node)
        for dist in distances.values():
            if dist in distance_counts:
                distance_counts[dist] += 1
            else:
                distance_counts[dist] = 1

    # 归一化得到概率分布
    total_pairs = n * (n - 1)  # 有向对
    distance_probs = {k: v / total_pairs for k, v in distance_counts.items()}
    return distance_probs

def set_font():
    if sys.platform == 'darwin':    # 表示是MacOS系统
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] # macOS系统请使用这行代码设置中文字体
    else:
        plt.rcParams['font.family'] = ['SimHei']     # Linux or Windows系统请使用这行代码设置中文字体
        plt.rcParams['axes.unicode_minus'] = False   # 防止负号'-'显示异常

# 主函数
def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    # Keep every generated artifact inside this assignment's results folder.
    import os
    os.chdir(OUTPUT_DIR)
    n = 100  # 100x100网格
    p = 0.1  # 重连概率，论文中通常使用0.1

    # 设置字体
    set_font()

    print("创建100x100的8邻居网格图...")
    start_time = time.time()
    G = create_lattice_graph(n)
    print(f"网格图创建完成，耗时: {time.time() - start_time:.2f}秒")
    print(f"初始边数: {G.number_of_edges()}")

    print("\n应用Watts-Strogatz模型进行重连...")
    start_time = time.time()
    G = watts_strogatz_rewire(G, p)
    print(f"重连完成，耗时: {time.time() - start_time:.2f}秒")
    print(f"重连后边数: {G.number_of_edges()}")

    print("\n计算距离分布...")
    start_time = time.time()
    distance_probs = calculate_distance_distribution(G)
    print(f"距离分布计算完成，耗时: {time.time() - start_time:.2f}秒")

    # 打印距离分布
    print("\n距离分布:")
    for dist in sorted(distance_probs.keys()):
        print(f"距离 {dist}: 概率 {distance_probs[dist]:.4f}")

    # 计算平均路径长度
    avg_path_length = nx.average_shortest_path_length(G)
    print(f"\n平均路径长度: {avg_path_length:.2f}")

    # 计算聚类系数
    clustering_coefficient = nx.average_clustering(G)
    print(f"平均聚类系数: {clustering_coefficient:.4f}")

    # 绘制距离分布图
    plt.figure(figsize=(10, 6))
    distances = sorted(distance_probs.keys())
    probabilities = [distance_probs[d] for d in distances]
    plt.bar(distances, probabilities)
    plt.xlabel('距离')
    plt.ylabel('概率')
    plt.title('Watts-Strogatz模型节点间距离分布')
    # 设置横坐标为0-10之间的所有整数
    plt.xticks(range(11))  # 0到10的整数
    plt.savefig('distance_distribution.png')
    print("\n距离分布图已保存为 distance_distribution.png")

    # 可视化网络（展示一个连续的网格区域）
    print("\n可视化网络...")
    # 选择一个连续的网格区域，保持8邻居结构
    region_size = 20  # 20x20的区域
    start_i, start_j = 40, 40  # 起始位置

    sample_nodes = []
    for i in range(start_i, start_i + region_size):
        for j in range(start_j, start_j + region_size):
            node = i * n + j
            sample_nodes.append(node)

    subgraph = G.subgraph(sample_nodes)

    plt.figure(figsize=(15, 12))
    # 创建网格布局，保持原始网格结构
    pos = {}
    for i in range(start_i, start_i + region_size):
        for j in range(start_j, start_j + region_size):
            node = i * n + j
            # 转换为相对坐标
            pos[node] = (j - start_j, start_i + region_size - 1 - i)

    # 绘制节点
    nx.draw_networkx_nodes(subgraph, pos, node_size=100, alpha=0.8)
    # 绘制边
    nx.draw_networkx_edges(subgraph, pos, width=1.0, alpha=0.6)
    plt.title('Watts-Strogatz网络可视化（20x20区域）')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('network_visualization.png', dpi=300)
    print("网络可视化图已保存为 network_visualization.png")

    # 绘制原始网格结构用于对比
    print("\n绘制原始网格结构...")
    # 创建原始网格图用于对比
    original_G = create_lattice_graph(region_size)
    original_pos = {}
    for i in range(region_size):
        for j in range(region_size):
            node = i * region_size + j
            original_pos[node] = (j, region_size - 1 - i)

    plt.figure(figsize=(15, 12))
    nx.draw_networkx_nodes(original_G, original_pos, node_size=100, alpha=0.8)
    nx.draw_networkx_edges(original_G, original_pos, width=1.0, alpha=0.6)
    plt.title('原始8邻居网格结构（20x20）')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('original_lattice.png', dpi=300)
    print("原始网格结构图已保存为 original_lattice.png")

    # 使用Plotly生成100x100的完整网络可视化
    print("\n使用Plotly生成100x100网络可视化...")
    # 创建网格布局位置
    plotly_pos = {}
    for i in range(n):
        for j in range(n):
            node = i * n + j
            plotly_pos[node] = (j, n - 1 - i)

    # 准备节点数据
    node_x = [plotly_pos[node][0] for node in G.nodes()]
    node_y = [plotly_pos[node][1] for node in G.nodes()]

    # 准备边数据
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = plotly_pos[edge[0]]
        x1, y1 = plotly_pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    # 创建边的轨迹
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # 创建节点的轨迹
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

    # 创建布局
    layout = go.Layout(
        title=dict(
            text='Watts-Strogatz网络可视化 (100x100)',
            font=dict(size=16)
        ),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    # 创建图表
    fig = go.Figure(data=[edge_trace, node_trace], layout=layout)

    # 保存为HTML文件
    fig.write_html('network_visualization_100x100.html')
    print("100x100网络可视化已保存为 network_visualization_100x100.html")

    # 返回结果数据
    return {
        'edges': G.number_of_edges(),
        'avg_path_length': avg_path_length,
        'clustering_coefficient': clustering_coefficient,
        'p': p,
        'distance_probs': distance_probs
    }

def write_result_to_md(results):
    """将运行结果写入 results/analysis.md 文件开头。"""
    md_file = OUTPUT_DIR / "analysis.md"

    # 读取现有内容
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    except FileNotFoundError:
        existing_content = ""

    # 构建新内容
    new_content = f"# Watts-Strogatz Network Analysis\n"
    new_content += f"- Grid size: 100x100\n"
    new_content += f"- Number of nodes: 10000\n"
    new_content += f"- Number of edges: {results['edges']}\n"
    new_content += f"- Average path length: {results['avg_path_length']:.2f}\n"
    new_content += f"- Average clustering coefficient: {results['clustering_coefficient']:.4f}\n"
    new_content += f"- Rewiring probability: {results['p']}\n\n"

    new_content += "## Distance Distribution\n"
    new_content += "| Distance | Probability |\n"
    new_content += "|----------|-------------|\n"
    for dist in sorted(results['distance_probs'].keys()):
        if dist <= 20:  # 只显示前20个距离
            new_content += f"| {dist} | {results['distance_probs'][dist]:.6f} |\n"
    new_content += "\n"

    new_content += "## Visualizations\n"
    new_content += "![Distance Distribution](distance_distribution.png)\n"
    new_content += "![Network Visualization (20x20)](network_visualization.png)\n"
    new_content += "![Original Lattice](original_lattice.png)\n"
    new_content += "[Interactive Network Visualization (100x100)](network_visualization_100x100.html)\n\n"

    # 添加现有内容
    new_content += existing_content

    # 写入文件
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"\n结果已写入 {md_file}")

if __name__ == "__main__":
    # 运行主函数并获取结果
    results = main()
    # 将结果写入result.md
    write_result_to_md(results)
