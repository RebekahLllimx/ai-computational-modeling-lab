import numpy as np
import sys
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def read_graph(file_path, max_lines=None):
    """读取图数据，返回优化的邻接表和节点列表"""
    # 首先收集所有节点
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

    # 为节点分配索引
    nodes = sorted(nodes)
    node_to_index = {node: i for i, node in enumerate(nodes)}
    n = len(nodes)

    # 构建优化的邻接表：使用numpy数组
    from_indices = []
    to_indices = []
    out_degrees = np.zeros(n, dtype=int)
    in_degrees = np.zeros(n, dtype=int)  # 初始化入度数组

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
                    in_degrees[to_idx] += 1  # 统计入度
                lines_read += 1

    # 转换为numpy数组
    from_indices = np.array(from_indices, dtype=int)
    to_indices = np.array(to_indices, dtype=int)

    return from_indices, to_indices, out_degrees, in_degrees, nodes, node_to_index

def pagerank(from_indices, to_indices, out_degrees, in_degrees, nodes, node_to_index, s=0.85, max_iterations=100, tolerance=1e-6):
    """计算PageRank值，实现同比缩减，等量补偿功能"""
    n = len(nodes)

    # 初始化PageRank值
    pr = np.ones(n, dtype=np.float64) / n

    # 预计算sink节点的索引
    sink_indices = np.where(out_degrees == 0)[0]
    num_sinks = len(sink_indices)

    # 预计算权重
    weights = 1.0 / out_degrees[from_indices]
    weights[out_degrees[from_indices] == 0] = 0  # 处理出度为0的情况

    for i in range(max_iterations):
        old_pr = pr.copy()

        # 计算sink节点的PR贡献
        sink_pr = np.sum(pr[sink_indices]) if num_sinks > 0 else 0

        # 初始化新的PR值
        new_pr = np.zeros(n, dtype=np.float64)

        # 使用numpy的向量化操作处理有出链接的节点
        # 计算每个边的贡献
        edge_contributions = s * pr[from_indices] * weights
        # 对每个目标节点累加贡献
        np.add.at(new_pr, to_indices, edge_contributions)

        # 处理sink节点和随机跳转
        new_pr += s * (sink_pr / n)
        new_pr += (1 - s) / n

        pr = new_pr

        # 检查收敛
        if np.linalg.norm(pr - old_pr) < tolerance:
            break

    # 将结果转换为节点到PR值的映射
    result = {node: pr[node_to_index[node]] for node in nodes}
    return result, in_degrees

def set_font():
    if sys.platform == 'darwin':    # 表示是MacOS系统
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] # macOS系统请使用这行代码设置中文字体
    else:
        plt.rcParams['font.family'] = ['SimHei']     # Linux or Windows系统请使用这行代码设置中文字体
        plt.rcParams['axes.unicode_minus'] = False   # 防止负号'-'显示异常

def visualize_in_degree_vs_pagerank(in_degrees, pr_values, nodes, node_to_index):
    set_font()
    """可视化节点入度与PageRank值的关系"""
    # 收集每个节点的入度和PageRank值
    in_degree_list = []
    pr_list = []

    for node in nodes:
        idx = node_to_index[node]
        in_degree_list.append(in_degrees[idx])
        pr_list.append(pr_values[node])

    # 创建散点图
    plt.figure(figsize=(12, 8))
    plt.scatter(in_degree_list, pr_list, alpha=0.5, s=10)
    plt.xscale('log')  # 使用对数刻度，因为入度分布通常是幂律的
    plt.yscale('log')  # 使用对数刻度，因为PageRank值也可能有较大差异
    plt.xlabel('In-Degree (log scale)')
    plt.ylabel('PageRank (log scale)')
    plt.title('Relationship between In-Degree and PageRank')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # 保存图表
    output_path = BASE_DIR / 'results' / 'in_degree_vs_pagerank.png'
    output_path.parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Visualization saved as '{output_path}'")

    # 显示图表
    plt.show()

if __name__ == "__main__":
    file_path = BASE_DIR / "data" / "web-Google.txt"
    # 读取所有行（不限制行数）
    from_indices, to_indices, out_degrees, in_degrees, nodes, node_to_index = read_graph(file_path)
    print(f"Total nodes: {len(nodes)}")
    print(f"Total edges: {len(from_indices)}")

    # 计算PageRank
    pr_values, in_degrees = pagerank(from_indices, to_indices, out_degrees, in_degrees, nodes, node_to_index, s=0.85)

    print("Top 10 PageRank values:")
    # 按PageRank值降序排序，输出前10个
    sorted_pr = sorted(pr_values.items(), key=lambda x: x[1], reverse=True)[:10]
    for node, pr in sorted_pr:
        print(f"Node {node}: {pr:.6f}")

    # 可视化入度与PageRank值的关系
    visualize_in_degree_vs_pagerank(in_degrees, pr_values, nodes, node_to_index)
