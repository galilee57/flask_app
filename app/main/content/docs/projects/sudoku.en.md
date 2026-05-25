---
title: 🌍 Project – Solving Algorithms
summary: English Version
---

# 🧠 Sudoku Solving Algorithms

Unlike the sliding puzzle problem — where the final state is already known — the important aspect here is not the path itself, but the final solution.  
However, choosing the right algorithm remains fundamental in order to optimize:

- performance,
- implementation complexity,
- search efficiency.

---

# 🧬 Genetic Approach

Genetic algorithms are particularly well suited for Sudoku solving.

The main idea is to:

1. generate candidate solutions by filling empty cells,
2. evaluate them using a cost function,
3. apply mutations whenever combinations fail.

The cost function evaluates:

- row conflicts,
- column conflicts,
- subgrid conflicts,
- overall grid consistency.

---

# ⚠️ The Local Optima Problem

One of the main difficulties in Sudoku — especially when very few digits are initially provided — is the presence of local optima.

These configurations appear promising but prevent the algorithm from progressing toward the global solution.

The challenge is therefore to balance:

| Exploration            | Exploitation                      |
| ---------------------- | --------------------------------- |
| Random behavior        | Deterministic behavior            |
| Discovery of new paths | Preservation of strong candidates |
| Diversity              | Optimization                      |

Exploitation makes it possible to preserve promising candidates that can later be reused whenever the search becomes blocked.

---

# 🔁 Local Backtracking

The implemented algorithm also supports **local backtracking**.

This means it can:

- step backward,
- abandon unpromising branches,
- restart from stronger candidates.

This hybrid strategy avoids **naive backtracking**, which is notoriously slow because it exhaustively explores every possible path.

---

# 🎯 Heuristic Selection

The algorithm first searches for:

> the cell with the best heuristic,
> namely the most constrained cell.

This strategy drastically reduces the search space.

---

# 🧪 Hybridization of Methods

The approach combines multiple techniques:

- heuristics,
- genetic generation,
- elitism,
- mutations,
- local backtracking.

The genetic mechanism works as follows:

1. generate multiple candidates,
2. preserve the best individuals (_elitism_),
3. cross the strongest candidates,
4. introduce random genomes to maintain diversity.

Maintaining diversity is essential to avoid local optima.

---

# 🧩 Sudoku Specificity

Sudoku has a particularly challenging property:

> a single incorrect digit may invalidate the entire grid.

This creates very deep local minima that are difficult to escape.

The problem therefore becomes both:

- a search problem,
- and a balance problem between exploration and exploitation.
