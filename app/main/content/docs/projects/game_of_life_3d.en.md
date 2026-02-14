---
title: 🧬 Project – 3D Game of Life (Three.js)
summary: English Version
---

**This project is a 3D version of the Game of Life, a cellular automaton.**

It is a system composed of cells arranged on a grid, whose state evolves over time according to simple, local rules.  
The visual design is inspired by a YouTube channel (link available in the footer).

🔍 **What is a cellular automaton?**

A cellular automaton is based on:
→ a grid (here in 3D),  
→ discrete states (alive / dead),  
→ a transition rule based solely on neighborhood conditions.

At each iteration, all cells are updated simultaneously by applying these rules, without any central control.

🌐 **Why 3D changes everything**

In 3D, we move from a simple checkerboard to a full volume: each cell has more neighbors, leading to richer dynamics and more “organic” structures.  
This results in even more striking emergent phenomena: stable patterns, oscillations, growth, or extinction depending on the parameters.

🎨 **Rendering and interaction with Three.js**

The project uses Three.js to visualize the simulation in real time:

→ each living cell is represented as a cube / voxel  
→ the 3D scene can be explored interactively (camera movement, zoom, rotation)  
→ the simulation highlights the connection between computational logic (the automaton) and graphical rendering (WebGL)

💡 **Why this project matters**

This project demonstrates how very simple local rules can generate global complexity. It provides a strong foundation for exploring more advanced simulation systems (ecosystems, diffusion models, collective behaviors, etc.).

It also represents a first step into 3D development — which, interestingly, can sometimes be easier to make responsive and visually clear than 2D.  
Libraries such as Three.js provide powerful built-in features that make object manipulation smooth and intuitive.
