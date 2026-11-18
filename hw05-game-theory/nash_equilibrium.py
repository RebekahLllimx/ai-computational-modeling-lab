import nashpy as nash
import numpy as np

# Song-licensing scenario: the rights holder is the row player.
li_matrix = np.array([
    [-2, 6],
    [-6, 4]
])

# The performer is the column player; columns mean proceed or switch.
shan_matrix = np.array([
    [-4, 8],
    [6, 4]
])

# Maritime-access scenario: the row player can counter-blockade or keep open.
us_matrix = np.array([
    [-5, 8],
    [2, 10]
])

# The column player can blockade or keep access open.
ir_matrix = np.array([
    [-10, 2],
    [12, 10]
])

# Compute equilibria for the two hypothetical payoff matrices.
li_shan_game = nash.Game(li_matrix, shan_matrix)
us_ir_game = nash.Game(us_matrix, ir_matrix)

print("=== Song-licensing scenario ===")
pure_equilibria = list(li_shan_game.support_enumeration())
for eq in pure_equilibria:
    li_strategy, shan_strategy = eq
    li_payoff = np.dot(li_strategy, np.dot(li_matrix, shan_strategy))
    shan_payoff = np.dot(shan_strategy, np.dot(shan_matrix.T, li_strategy))

    li_action = "enforce" if li_strategy[0] == 1 else "remain passive"
    shan_action = "switch" if shan_strategy[1] == 1 else "proceed"

    print(f"Strategies: rights holder: {li_action}; performer: {shan_action}")
    print(f"Payoffs: rights holder: {li_payoff}; performer: {shan_payoff}")

print("\n=== Maritime-access scenario ===")
pure_equilibria_ho = list(us_ir_game.support_enumeration())
for eq in pure_equilibria_ho:
    us_strategy, ir_strategy = eq
    us_payoff = np.dot(us_strategy, np.dot(us_matrix, ir_strategy))
    ir_payoff = np.dot(ir_strategy, np.dot(ir_matrix.T, us_strategy))

    us_action = "counter-blockade" if us_strategy[0] == 1 else "open"
    ir_action = "blockade" if ir_strategy[0] == 1 else "open"

    print(f"Strategies: row: {us_action}; column: {ir_action}")
    print(f"Payoffs: row: {us_payoff}; column: {ir_payoff}")
