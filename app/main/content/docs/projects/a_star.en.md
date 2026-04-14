---
title: 🧩 Project – Sliding Puzzle (A* Algorithm)
summary: English Version
---

**This project is an interactive application designed to solve the sliding puzzle (8-puzzle) using the A\* algorithm.**
The goal is to rearrange the tiles to reach the final configuration in the minimum number of moves.

The main feature of this project is the visualization of the solving process, including state exploration and the search tree.

⚙️ **Technical overview**

State representation
→ The board is represented as an array (list of 9 elements).
→ The empty tile is represented by 0.

Neighbor generation
→ Possible moves are computed (up, down, left, right).
→ Each move generates a new puzzle state.

A\* algorithm
→ A priority queue (heap) is used to explore states.
→ Cost function:  
 g(n) = number of moves  
 h(n) = Manhattan distance  
 f(n) = g(n) + h(n)

→ The algorithm always selects the state with the lowest total cost.

Solution reconstruction
→ Once the goal state is reached, the path is reconstructed using parent links.
→ The solution is the sequence of states from start to goal.

Dynamic user interface
→ The board is generated dynamically in JavaScript.
→ The user can shuffle, edit, or solve the puzzle.

Tree visualization
→ Explored nodes are displayed by depth (g).
→ Each state is shown as a mini grid.
→ The user can toggle the tree and replay the solution.

Validation & interaction
→ The puzzle solvability is checked (inversion parity).
→ User feedback (messages, animation, number of moves).

💡 **Project value**

This project highlights:
→ implementation of a search algorithm (A\*)
→ use of an admissible heuristic (Manhattan distance)
→ manipulation of data structures (heap, implicit graph)
→ educational visualization of an algorithm
→ user interaction management (editing, animation, replay)

It combines algorithmics, interactive UI, and real-time visualization of a search process.
