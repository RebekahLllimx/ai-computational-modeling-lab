import nashpy as nash
import numpy as np

# 定义"李白"侵权事件的收益矩阵
# 李荣浩的收益矩阵（行玩家）
li_matrix = np.array([
    [-2, 6],  # 强硬维权：面对侵权演唱(-2)，面对合规替换(6)
    [-6, 4]   # 放任沉默：面对侵权演唱(-6)，面对合规替换(4)
])

# 单依纯的收益矩阵（列玩家）
shan_matrix = np.array([
    [-4, 8],  # 侵权演唱：面对强硬维权(-4)，面对放任沉默(8)
    [6, 4]    # 合规替换：面对强硬维权(6)，面对放任沉默(4)
])

# 定义霍尔木兹海峡事件的收益矩阵
# 美国的收益矩阵（行玩家）
us_matrix = np.array([
    [-5, 8],  # 对等封锁：面对伊朗封锁(-5)，面对伊朗开放(8)
    [2, 10]   # 保持开放：面对伊朗封锁(2)，面对伊朗开放(10)
])

# 伊朗的收益矩阵（列玩家）
ir_matrix = np.array([
    [-10, 2],  # 封锁海峡：面对美国封锁(-10)，面对美国开放(2)
    [12, 10]   # 保持开放：面对美国封锁(12)，面对美国开放(10)
])

# 创建博弈对象
li_shan_game = nash.Game(li_matrix, shan_matrix)
us_ir_game = nash.Game(us_matrix, ir_matrix)

# 求解"李白"侵权事件的纯策略纳什均衡
print("=== '李白'侵权事件博弈求解 ===")
pure_equilibria = list(li_shan_game.support_enumeration())
for eq in pure_equilibria:
    li_strategy, shan_strategy = eq
    li_payoff = np.dot(li_strategy, np.dot(li_matrix, shan_strategy))
    shan_payoff = np.dot(shan_strategy, np.dot(shan_matrix.T, li_strategy))

    # 转换策略数组为真实策略名称
    li_action = "强硬维权" if li_strategy[0] == 1 else "放任沉默"
    shan_action = "合规替换" if shan_strategy[1] == 1 else "侵权演唱"

    print(f"策略组合: (李荣浩: {li_action}, 单依纯: {shan_action})")
    print(f"收益: (李荣浩: {li_payoff}, 单依纯: {shan_payoff})")

# 求解霍尔木兹海峡事件的纯策略纳什均衡
print("\n=== 霍尔木兹海峡双重封锁事件博弈求解 ===")
pure_equilibria_ho = list(us_ir_game.support_enumeration())
for eq in pure_equilibria_ho:
    us_strategy, ir_strategy = eq
    us_payoff = np.dot(us_strategy, np.dot(us_matrix, ir_strategy))
    ir_payoff = np.dot(ir_strategy, np.dot(ir_matrix.T, us_strategy))

    # 转换策略数组为真实策略名称
    us_action = "对等封锁" if us_strategy[0] == 1 else "保持开放"
    ir_action = "封锁海峡" if ir_strategy[0] == 1 else "保持开放"

    print(f"策略组合: (美国: {us_action}, 伊朗: {ir_action})")
    print(f"收益: (美国: {us_payoff}, 伊朗: {ir_payoff})")