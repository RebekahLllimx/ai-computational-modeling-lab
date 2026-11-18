# Two games: licensing and maritime access

These two 2 x 2 games use hypothetical utilities to examine best responses,
Nash equilibria, and Pareto efficiency. Their numbers and scenarios are
modeling assumptions, not measurements of actual participants' preferences
or findings about real-world conduct.

## 1. Song licensing

The row player is a rights holder who can enforce a claim or remain passive.
The column player is a performer who can proceed with a disputed performance
or switch to an authorized alternative. Payoffs are ordered as
`(rights holder, performer)`:

| | Proceed | Switch |
| --- | ---: | ---: |
| Enforce | (-2, -4) | (6, 8) |
| Remain passive | (-6, 6) | (4, 4) |

The utilities reflect assumed trade-offs involving control of the work,
reputation, publicity, and the ability to perform. For example, the model
assigns the rights holder `3 + 2 - 5 - 2 = -2` when enforcement and a disputed
performance coincide; the performer's assumed payoff in that cell is
`3 - 5 - 2 = -4`. The other cells similarly combine hypothetical benefits
and costs rather than estimates from observations.

Enforcement is strictly dominant for the rights holder: `-2 > -6` if the
performer proceeds, and `6 > 4` if the performer switches. Given enforcement,
the performer's best response is to switch (`8 > -4`). The unique pure-strategy
Nash equilibrium is therefore **(enforce, switch)**, with payoffs `(6, 8)`.
It is also Pareto efficient within this payoff matrix.

The model is a simultaneous one-shot game. Questions about incomplete
information, delegation of licensing checks, or later negotiation would
require additional assumptions and a different game structure.

## 2. Maritime access

The row player chooses either a counter-blockade or keeping access open; the
column player chooses a blockade or open access. Payoffs are ordered as
`(row player, column player)`:

| | Blockade | Open |
| --- | ---: | ---: |
| Counter-blockade | (-5, -10) | (8, 2) |
| Open | (2, 12) | (10, 10) |

The numerical utilities summarize assumed strategic, economic, and conflict
costs. For example, the counter-blockade/blockade cell assigns `-3 - 1 - 1`
to the row player and `-6 - 3 - 1` to the column player. The open/blockade
cell assigns `-1 + 2 + 1 = 2` and `4 + 6 + 2 = 12`, respectively. These are
illustrative scores, not observed economic or military outcomes.

Open access is strictly dominant for the row player: `2 > -5` when the column
player blockades, and `10 > 8` when the column player remains open. Its best
response to an open row player is a blockade (`12 > 10`). The unique
pure-strategy Nash equilibrium is **(open, blockade)**, with payoffs `(2, 12)`.

The **(open, open)** outcome has the highest sum of utilities, `20`, compared
with `14` at the equilibrium. Both `(open, open)` and `(open, blockade)` are
Pareto efficient in this matrix: moving between them benefits one player while
reducing the other's payoff. A repeated interaction or negotiation could have
different equilibria, but those dynamics are not modeled here.

## Comparison

Both games give the row player a strictly dominant action and have a unique
pure-strategy equilibrium. The licensing equilibrium is `(6, 8)`; the maritime
equilibrium is `(2, 12)`, while another outcome maximizes the payoff sum. The
contrast illustrates how the same equilibrium concept can yield different
distributions of utility under different assumptions.

Run `python nash_equilibrium.py` to compute the equilibria with `nashpy`.
