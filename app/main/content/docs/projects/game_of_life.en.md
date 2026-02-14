---
title: 🧬 Project – Game of Life
summary: English Version
---

**This project is an implementation of the Game of Life, originally devised by John Conway.**

It is a cellular automaton — a system composed of cells arranged on a grid, whose state evolves over time according to simple, local rules.

🔍 **What is a cellular automaton?**

A cellular automaton is based on three fundamental principles:
→ a grid of cells (often 2D)  
→ a discrete state for each cell (alive or dead)  
→ local rules that determine a cell’s future state based on its neighbors

At each iteration, the same rules are applied simultaneously across the entire grid, without any central control.

In the Game of Life, the rules are intentionally minimal:
→ a cell survives or dies depending on the number of living neighbors  
→ a dead cell can “come to life” if specific conditions are met

💡 **Why this project is interesting**

Despite extremely simple rules, the system generates complex and unpredictable behaviors: stable structures, oscillators, moving patterns, and interacting formations.

It is an excellent example of emergent complexity, where rich phenomena arise without explicitly programming global behavior.

This project allows you to:
→ understand how complex systems can emerge from local rules  
→ explore concepts such as simulation, iteration, and state transitions  
→ manipulate grids, neighborhoods, and synchronized updates  
→ connect computer science, mathematics, and the modeling of living systems

🧠 **Broader perspective**

The Game of Life is often used as an entry point into complex systems modeling, simulation theory, systems thinking, and self-organization.
This project naturally fits into a broader simulation-oriented approach, aligned with more ambitious future developments.

One of the main challenges is that meaningful pattern formation requires relatively large grids to allow complex structures to emerge and evolve.
To make the project responsive, I implemented adjustable grid sizing, allowing the grid dimensions to adapt to the screen size while maintaining visual clarity and performance.
