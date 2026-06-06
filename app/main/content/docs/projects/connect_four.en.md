---
title: 🌍 Connect Four and Deterministic Algorithms
summary: English Version
---

**Connect Four and Artificial Intelligence**

This project introduces a new challenge compared to solving **Sudoku** or the **Sliding Puzzle**: it is a **two-player adversarial game**.

The rules are simple and fully known. The game is **deterministic**, meaning that no random event occurs during a match. As a result, it is possible to anticipate the consequences of every move.

A **Reinforcement Learning** approach could be considered. However, reaching a strong playing level would require generating and analyzing millions, or even billions, of games. This approach is therefore not particularly well suited for an educational project.

**The Minimax Algorithm**

The artificial intelligence implemented here relies on the **Minimax** algorithm.

The idea is to build a **game tree of possible moves** up to a given depth. The algorithm alternates between simulating the AI's moves and the opponent's moves in order to anticipate the consequences of every decision.

▶︎ The AI tries to **MAXimize** its chances of winning.  
▶︎ It assumes that the opponent will try to **MINimize** those same chances.

The name **Minimax** comes directly from this strategy.

**Heuristic Evaluation**

In practice, it is usually impossible to explore the entire game tree. An evaluation function, called a **heuristic**, is therefore used to estimate the quality of a given position.

This heuristic assigns scores according to several criteria:

▶︎ creating a line of two pieces;  
▶︎ creating a line of three pieces;  
▶︎ controlling the center column;  
▶︎ blocking an opponent's threat;  
▶︎ creating a winning position;  
▶︎ avoiding an immediate loss.

The quality of this evaluation function largely determines the overall performance of the artificial intelligence.

**Problem Complexity**

Connect Four has been completely solved mathematically. It is estimated that there are approximately **4 × 10¹² different board positions**.

Exhaustively exploring this search space is unrealistic on a personal computer. The number of positions to analyze grows exponentially with the search depth.

**Optimization: Alpha-Beta Pruning**

To speed up computations, an optimized version of Minimax called **Alpha-Beta Pruning** is used.

This technique eliminates many branches of the game tree that cannot possibly lead to a better solution. As a result, the computation time is significantly reduced without affecting the final decision.

**Why Not Use MCTS?**

Another family of algorithms, **Monte Carlo Tree Search (MCTS)**, could be used to strengthen the artificial intelligence.

MCTS is particularly effective when:

▶︎ the search space is extremely large;  
▶︎ the evaluation function is difficult to design;  
▶︎ the game has a very high strategic complexity.

It is notably used in games such as **Go**.

In the case of Connect Four, a **Minimax algorithm with Alpha-Beta pruning**, combined with a good heuristic and a sufficient search depth, already provides excellent performance while remaining relatively easy to understand and
