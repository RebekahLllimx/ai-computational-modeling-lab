import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import random
from collections import defaultdict
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent / "results"


class WSKNetwork:
    def __init__(self, n, k, alpha):
        """
        初始化WSK网络
        n: 网格大小 (n x n)
        k: 每个节点的近邻连接数
        alpha: 聚类指数
        """
        self.n = n
        self.k = k
        self.alpha = alpha
        self.N = n * n  # 总节点数
        self.G = nx.Graph()
        self._build_network()

    def _node_to_pos(self, node):
        """将节点ID转换为网格坐标"""
        return (node // self.n, node % self.n)

    def _pos_to_node(self, x, y):
        """将网格坐标转换为节点ID"""
        return x * self.n + y

    def _manhattan_distance(self, pos1, pos2):
        """计算曼哈顿距离"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def _build_network(self):
        """构建WSK网络"""
        # 添加所有节点
        for i in range(self.N):
            self.G.add_node(i)

        # 添加短程连接（近邻）
        for node in range(self.N):
            x, y = self._node_to_pos(node)
            # 连接到k个最近的邻居
            neighbors = []
            # 上、下、左、右四个方向
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dx, dy in directions:
                for d in range(1, self.k//4 + 1):
                    nx = (x + dx * d) % self.n
                    ny = (y + dy * d) % self.n
                    neighbor_node = self._pos_to_node(nx, ny)
                    if neighbor_node != node:
                        neighbors.append(neighbor_node)
            # 添加这些连接
            for neighbor in neighbors[:self.k]:
                self.G.add_edge(node, neighbor)

        # 添加远程连接
        for node in range(self.N):
            x, y = self._node_to_pos(node)
            # 计算到所有其他节点的距离和概率
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

            # 归一化概率
            for other_node in probabilities:
                probabilities[other_node] /= total_prob

            # 随机选择一个远程连接
            if probabilities:
                selected_node = random.choices(
                    list(probabilities.keys()),
                    weights=list(probabilities.values()),
                    k=1
                )[0]
                self.G.add_edge(node, selected_node)

    def get_distance_distribution(self):
        """计算距离分布"""
        # 随机选择一些节点对来计算距离
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
        """计算朋友关系概率与rank的关系"""
        # 计算每个节点的所有邻居距离
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

        # 计算概率
        rank_prob = []
        # 按距离排序
        sorted_distances = sorted(distance_counts.keys())
        for i, r in enumerate(sorted_distances):
            rank = i + 1
            prob = distance_counts[r] / total_pairs
            rank_prob.append((rank, prob))

        return rank_prob

    def visualize(self):
        """可视化网络"""
        pos = {node: self._node_to_pos(node) for node in self.G.nodes()}
        plt.figure(figsize=(10, 10))
        nx.draw(self.G, pos, node_size=10, alpha=0.5, with_labels=False)
        plt.title(f"WSK Network (n={self.n}, k={self.k}, alpha={self.alpha})")
        plt.savefig("network_visualization.png")
        plt.show()

def fit_power_law(rank_prob):
    """拟合幂律分布并估计q值"""
    ranks, probs = zip(*rank_prob)

    # 转换为数组
    ranks = np.array(ranks)
    probs = np.array(probs)

    # 取对数
    log_ranks = np.log(ranks)
    log_probs = np.log(probs)

    # 线性回归
    coefficients = np.polyfit(log_ranks, log_probs, 1)
    q = -coefficients[0]  # 幂次指数

    return q, coefficients

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    # Keep every generated artifact inside this assignment's results folder.
    import os
    os.chdir(OUTPUT_DIR)
    # 参数设置
    n = 100  # 网格大小
    k = 4   # 近邻连接数
    alpha = 2.0  # 聚类指数

    # 构建网络
    print("Building WSK network...")
    network = WSKNetwork(n, k, alpha)
    print(f"Network built with {network.N} nodes and {network.G.number_of_edges()} edges")

    # 可视化网络
    network.visualize()

    # 计算距离分布
    print("Calculating distance distribution...")
    distances = network.get_distance_distribution()

    # 绘制距离分布图
    plt.figure(figsize=(10, 6))
    plt.hist(distances, bins=20, alpha=0.75)
    plt.title("Distance Distribution")
    plt.xlabel("Distance")
    plt.ylabel("Frequency")
    plt.xticks(range(11))  # 0到10的整数
    plt.savefig("distance_distribution.png")
    plt.show()

    # 计算rank概率关系
    print("Calculating rank-probability relationship...")
    rank_prob = network.get_rank_probability()

    # 拟合幂律
    q, coefficients = fit_power_law(rank_prob)
    print(f"Estimated q value: {q:.4f}")

    # 绘制rank概率关系
    ranks, probs = zip(*rank_prob)
    plt.figure(figsize=(10, 6))
    plt.loglog(ranks, probs, 'o', label='Data')

    # 绘制拟合线
    fit_ranks = np.logspace(np.log10(min(ranks)), np.log10(max(ranks)), 100)
    fit_probs = np.exp(coefficients[1]) * (fit_ranks ** (-q))
    plt.loglog(fit_ranks, fit_probs, '-r', label=f'Fit: P(r) ∝ r^(-{q:.4f})')

    plt.title("Rank-Probability Relationship")
    plt.xlabel("Rank (r)")
    plt.ylabel("Probability P(r)")
    plt.legend()
    plt.grid(True, which="both", ls="--")
    plt.savefig("rank_probability.png")
    plt.show()

    # 保存结果
    with open("result.md", "w") as f:
        f.write(f"# WSK Network Analysis\n")
        f.write(f"- Grid size: {n}x{n}\n")
        f.write(f"- Number of nodes: {network.N}\n")
        f.write(f"- Number of edges: {network.G.number_of_edges()}\n")
        f.write(f"- Clustering exponent alpha: {alpha}\n")
        f.write(f"- Estimated q value: {q:.4f}\n")

        # 添加网络可视化图片
        f.write("\n## Network Visualization\n")
        f.write("![Network Visualization](network_visualization.png)\n")

        # 添加距离分布图
        f.write("\n## Distance Distribution\n")
        f.write("![Distance Distribution](distance_distribution.png)\n")

        # 添加rank-概率关系图
        f.write("\n## Rank-Probability Relationship\n")
        f.write("![Rank-Probability Relationship](rank_probability.png)\n")

        f.write("\n## Rank-Probability Data\n")
        f.write("| Rank | Probability |\n")
        f.write("|------|-------------|\n")
        for rank, prob in rank_prob:
            f.write(f"| {rank} | {prob:.6f} |\n")

if __name__ == "__main__":
    main()
