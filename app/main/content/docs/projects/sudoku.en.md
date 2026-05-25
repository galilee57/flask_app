---
title: 🌍 Project – Solving Algorithms
summary: English Version
---

# 🧠 Sudoku Solving Algorithms

Unlike the sliding puzzle — where the final state is known in advance — what matters here is not the path itself, but the final solution.

However, the choice of algorithm remains fundamental in order to optimize:
• performance,
• implementation complexity,
• exploration quality.

---

# 🧬 Genetic Approach

The genetic algorithm is a particularly suitable approach.

The principle consists of:
• generating candidates by filling empty cells,
• evaluating their quality through a cost function,
• applying mutations whenever combinations fail.

The cost function measures the number of conflicts and validates rows, columns, and subgrids.

---

# ⚠️ The Local Optimum Problem

The main difficulty of Sudoku — especially when very few numbers are initially known — lies in the existence of local optima.

These configurations may appear promising but prevent the algorithm from progressing toward the global solution. The challenge is therefore to balance:
• **Exploration**: randomness, discovery of new paths, diversity
• **Exploitation**: deterministic behavior, preservation of the best candidates, optimization

Exploitation makes it possible to preserve promising candidates and return to them if the search becomes stuck.

---

# 🔁 Local Backtracking

The implemented algorithm also supports **local backtracking**.

This means it can:
• step backward,
• abandon an unpromising branch,
• restart from a better candidate.

This hybrid approach avoids **naive backtracking**, which is particularly slow because it systematically explores every possible path.

---

# 🎯 Selection Heuristic

The algorithm begins by searching for:
• the cell with the best heuristic,
• meaning the most constrained cell.

This strategy significantly reduces the number of possibilities to explore.

---

# 🧪 Hybridization of Methods

The implemented approach combines several techniques:
• heuristics,
• genetic generation,
• elitism,
• mutations,
• local backtracking.

The genetic mechanism works as follows:

• generation of multiple candidates,
• preservation of the best individuals (_elitism_),
• crossover between the best candidates,
• introduction of random genomes to maintain diversity.

This diversity is essential to avoid local optima.

---

# 🧩 Sudoku Specificity

Sudoku has an important characteristic: a single error in one cell can invalidate the entire grid.
This creates very deep local minima that are difficult to escape from.

The problem therefore becomes both:
• a search problem,
• and a balance problem between exploration and exploitation.
