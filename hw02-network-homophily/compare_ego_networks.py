"""
一句话概括：批量扫描并自动分析 Facebook 数据集中多个中心节点（ego-network）的性别同质性，并进行横向对比。
输入数据：data/facebook/ 目录下的多个 ego 网络的特征名定义（.featnames）、节点特征（.feat, .egofeat）和连边（.edges）文件。
输出结果：格式化的对比输出，展示各个 ego 网络的有效边数、实际同质性比例、期望基准和最终的同质性指数。
核心逻辑概述：自动发现数据集中的所有 ego 节点，动态解析每个网络因匿名化而发生偏移的性别特征列索引。在重构无向子网与计算期望概率时，严格按照活跃边集合约束拓扑，并采用全量节点规模为基准，以提供高度精确的横向宏观对比。
"""

import os
import glob

def get_gender_feature_indices(featnames_file):
    """
    功能描述：动态解析特定 ego 网络的特征名映射文件，找出代表性别的特征索引。
    参数说明：
        - featnames_file (str): 特征维度名称映射文件（.featnames）的路径。
    返回值说明：
        - list: 包含性别特征对应整数索引的列表；若未找到则返回空列表。
    处理逻辑：
        逐行读取文件，通过关键词匹配识别出表示性别的匿名化特征，并提取其所在的列号。这消除了不同子网因匿名混淆而造成的硬编码失效问题。
    """
    indices = []
    if not os.path.exists(featnames_file):
        return indices

    with open(featnames_file, 'r') as f:
        for line in f:
            if 'gender' in line.lower():
                parts = line.split()
                if parts:
                    try:
                        indices.append(int(parts[0]))
                    except ValueError:
                        continue
    return indices

def load_network_data(ego_id, base_dir, gender_indices):
    """
    功能描述：加载并重构单个 ego 网络的节点性别特征与去重无向连边。
    参数说明：
        - ego_id (str): 中心节点的 ID。
        - base_dir (str): 数据集所在的基础目录。
        - gender_indices (list): 当前网络中代表性别的列索引列表（通常为两个）。
    返回值说明：
        - tuple: (edges, gender_map)，其中 edges 是无向边集合，gender_map 是节点到性别的映射字典。
    处理逻辑：
        严格对齐中心节点与邻居节点的特征提取切片（剔除 ID 偏移）。通过数值比较清洗边数据确保无向性，并仅选取边文件中活跃的节点与中心节点建立星型连接。
    """
    feat_file = os.path.join(base_dir, f'{ego_id}.feat')
    egofeat_file = os.path.join(base_dir, f'{ego_id}.egofeat')
    edges_file = os.path.join(base_dir, f'{ego_id}.edges')

    gender_map = {}
    edges = set()

    if not gender_indices:
        return edges, gender_map

    idx_1 = gender_indices[0]
    idx_2 = gender_indices[1] if len(gender_indices) > 1 else -1
    max_idx = max(gender_indices)

    # 1. 提取中心节点性别（修复了由前置 ID 导致的索引偏移）
    if os.path.exists(egofeat_file):
        with open(egofeat_file, 'r') as f:
            parts = f.read().strip().split()
            if parts:
                features = parts[1:] # 强制切片对齐
                if len(features) > max_idx:
                    if features[idx_1] == '1':
                        gender_map[str(ego_id)] = 'type_A'
                    elif idx_2 != -1 and features[idx_2] == '1':
                        gender_map[str(ego_id)] = 'type_B'
                    else:
                        gender_map[str(ego_id)] = 'unknown'

    # 2. 提取邻居节点性别
    if os.path.exists(feat_file):
        with open(feat_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if not parts: continue
                node_id = parts[0]
                features = parts[1:] # 统一特征切片
                if len(features) > max_idx:
                    if features[idx_1] == '1':
                        gender_map[node_id] = 'type_A'
                    elif idx_2 != -1 and features[idx_2] == '1':
                        gender_map[node_id] = 'type_B'
                    else:
                        gender_map[node_id] = 'unknown'

    # 3. 构建无向连边与 Ego 约束拓扑
    nodes_in_edges = set()
    if os.path.exists(edges_file):
        with open(edges_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    u, v = parts[0], parts[1]
                    nodes_in_edges.add(u)
                    nodes_in_edges.add(v)
                    # 采用整数大小比较统一元组排序
                    if int(u) < int(v):
                        edges.add((u, v))
                    else:
                        edges.add((v, u))

    # 仅向在 edges 文件中出现的活跃节点发起 Ego 星型连接
    ego_str = str(ego_id)
    for node in nodes_in_edges:
        if int(ego_str) < int(node):
            edges.add((ego_str, node))
        else:
            edges.add((node, ego_str))

    return edges, gender_map

def analyze_homophily(edges, gender_map):
    """
    功能描述：计算单个子网的实际同构连接占比、随机期望值与同质性指数。
    参数说明：
        - edges (set): 网络的去重无向连边集合。
        - gender_map (dict): 节点的性别字典。
    返回值说明：
        - dict: 包含同质性核心指标的字典；若无有效数据则返回 None。
    处理逻辑：
        剔除包含未知属性节点的无效边计算实际同质率。随后基于包含“未知属性”节点在内的全局网络规模，计算随机匹配概率并得出最终指数。
    """
    valid_edges = 0
    same_gender_edges = 0

    # 统计不同类型边的数量
    type_a_to_a = 0
    type_b_to_b = 0
    type_a_to_b = 0
    type_b_to_a = 0
    unknown_edges = 0

    for u, v in edges:
        g_u = gender_map.get(u, 'unknown')
        g_v = gender_map.get(v, 'unknown')

        if g_u == 'unknown' or g_v == 'unknown':
            unknown_edges += 1
            continue

        valid_edges += 1

        # 统计不同类型的边
        if g_u == 'type_A' and g_v == 'type_A':
            same_gender_edges += 1
            type_a_to_a += 1
        elif g_u == 'type_B' and g_v == 'type_B':
            same_gender_edges += 1
            type_b_to_b += 1
        elif g_u == 'type_A' and g_v == 'type_B':
            type_a_to_b += 1
        elif g_u == 'type_B' and g_v == 'type_A':
            type_b_to_a += 1

    total_nodes = len(gender_map)
    # 增加空数据拦截避免零除崩溃
    if total_nodes == 0:
        return None

    actual_homophily = same_gender_edges / valid_edges if valid_edges > 0 else 0

    type_a_count = list(gender_map.values()).count('type_A')
    type_b_count = list(gender_map.values()).count('type_B')
    unknown_count = list(gender_map.values()).count('unknown')

    # 计算期望时，严格采用全量节点规模（total_nodes）作为分母
    p_a = type_a_count / total_nodes
    p_b = type_b_count / total_nodes
    expected_homophily = (p_a ** 2) + (p_b ** 2)

    homophily_index = actual_homophily - expected_homophily

    return {
        'valid_edges': valid_edges,
        'actual_homophily': actual_homophily,
        'expected_homophily': expected_homophily,
        'homophily_index': homophily_index,
        'total_nodes': total_nodes,
        'type_a_count': type_a_count,
        'type_b_count': type_b_count,
        'unknown_count': unknown_count,
        'same_gender_edges': same_gender_edges,
        'type_a_to_a': type_a_to_a,
        'type_b_to_b': type_b_to_b,
        'type_a_to_b': type_a_to_b,
        'type_b_to_a': type_b_to_a,
        'unknown_edges': unknown_edges,
        'p_a': p_a,
        'p_b': p_b
    }

def main():
    """
    功能描述：程序的主执行入口，协调批量扫描与对比输出。
    参数说明：无。
    返回值说明：无。
    处理逻辑：动态获取当前执行路径以规避跨目录调用异常。搜索所有中心节点文件，循环执行解析与计算，最后输出格式化的统计报表。
    """
    # 动态获取当前脚本所在目录的绝对路径并拼接数据文件夹路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, 'data', 'facebook')

    search_pattern = os.path.join(base_dir, '*.egofeat')
    ego_files = glob.glob(search_pattern)

    ego_ids = []
    for f in ego_files:
        filename = os.path.basename(f)
        ego_id = filename.split('.')[0]
        ego_ids.append(ego_id)

    ego_ids.sort(key=lambda x: int(x))

    if not ego_ids:
        print(f"未在路径 {base_dir} 下找到数据文件。请检查目录结构。")
        return

    print(f"{'Ego ID':<8} | {'有效边数':<10} | {'实际同质性':<12} | {'期望基准':<10} | {'同质性指数':<10} | {'倾向结论'}")
    print("-" * 80)

    for ego_id in ego_ids:
        featnames_file = os.path.join(base_dir, f'{ego_id}.featnames')
        gender_indices = get_gender_feature_indices(featnames_file)

        if not gender_indices:
            print(f"{ego_id:<8} | 缺少性别特征定义，跳过分析")
            continue

        edges, gender_map = load_network_data(ego_id, base_dir, gender_indices)
        results = analyze_homophily(edges, gender_map)

        if results:
            idx = results['homophily_index']
            trend = "同质性倾向" if idx > 0.01 else "逆同质性/随机" if idx < -0.01 else "随机分布"

            # 输出详细的调试文本
            print(f"\n=== 分析 ego ID: {ego_id} ===")
            print(f"总节点数: {results['total_nodes']}")
            print(f"  - type_A节点数: {results['type_a_count']}")
            print(f"  - type_B节点数: {results['type_b_count']}")
            print(f"  - 未知性别节点数: {results['unknown_count']}")
            print(f"  - type_A比例 (p_a): {results['p_a']:.4f}")
            print(f"  - type_B比例 (p_b): {results['p_b']:.4f}")

            print(f"\n边统计:")
            print(f"  - 总边数: {len(edges)}")
            print(f"  - 有效边数: {results['valid_edges']}")
            print(f"  - 未知性别边数: {results['unknown_edges']}")
            print(f"  - type_A到type_A边数: {results['type_a_to_a']}")
            print(f"  - type_B到type_B边数: {results['type_b_to_b']}")
            print(f"  - type_A到type_B边数: {results['type_a_to_b']}")
            print(f"  - type_B到type_A边数: {results['type_b_to_a']}")
            print(f"  - 同质边总数: {results['same_gender_edges']}")

            print(f"\n同质性计算:")
            print(f"  - 实际同质性比例: {results['actual_homophily']:.4f}")
            print(f"  - 期望同质性: {results['expected_homophily']:.4f}")
            print(f"  - 同质性指数: {idx:.4f}")
            print(f"  - 结果: {trend}")

            # 保持原有的表格格式输出
            print(f"{ego_id:<8} | {results['valid_edges']:<10} | {results['actual_homophily']:<12.4f} | {results['expected_homophily']:<10.4f} | {idx:<10.4f} | {trend}")
        else:
            print(f"\n=== 分析 ego ID: {ego_id} ===")
            print("缺少有效的连边或节点属性，跳过分析")
            print(f"{ego_id:<8} | 缺少有效的连边或节点属性，跳过分析")

if __name__ == '__main__':
    main()