---
title: 🐍 Project – Snake, A* and Reinforcement Learning
summary: English Version
---

**This project revisits Snake with an isometric board and three game modes: human control, A\* pathfinding, and a neural network trained through reinforcement learning.**

The goal is to eat fruit to grow the snake while avoiding the edges and its own body. Each fruit adds one point. The project lets users observe and compare two ways of building an AI: computing a path or learning how to choose movements.

🎮 **Gameplay & interface**

The game uses a 20 × 20 grid, drawn in isometric perspective on a JavaScript Canvas. This perspective changes the visual representation, while the underlying logic remains a grid with four directions.

→ In Human mode, the arrow keys steer the snake; markers around the board show the corresponding movement.\
→ The slider adjusts speed from slow to fast, including during play. Human mode has a slower speed range than the AI modes.\
→ Play starts movement, Stop pauses it, and Reset starts a new game.\
→ On wide screens, the board and controls sit side by side; on smaller screens, they stack vertically.

🧭 **A\* mode: computing a path**

At each move, A\* searches for a path to the fruit, treating the snake’s current body as an obstacle.

→ A priority queue selects which cells to explore.\
→ The cost combines the length of the path already travelled and the Manhattan distance to the fruit.\
→ The first move along the resulting path determines the snake’s direction.

This approach can reach the fruit when a path is available. However, it does not simulate future changes to the snake’s body: a short path can lead to a situation from which the snake cannot escape.

🧠 **DQN mode: learning from experience**

DQN mode uses a NumPy neural network with **11 inputs, 128 hidden neurons, and 3 outputs**. It receives immediate dangers, the snake’s direction, and the fruit’s relative position. It then estimates the value of three actions: continue straight, turn right, or turn left.

Training takes place in games that are independent of the displayed game:

→ The snake explores actions, then gradually relies more on the network’s decisions.\
→ Experiences are stored in replay memory and reused in batches.\
→ Double DQN separates next-action selection from evaluation by a target network.\
→ The Adam optimizer updates the network’s parameters.

Eating fruit gives a reward of +10; a collision gives −10, and an ordinary move gives −0.01. An additional signal based on distance to the fruit guides learning. Games that run too long without fruit are terminated during training.

Once trained, the network plays without random exploration and does not learn during the web game. **The DQN chooses its own actions: it does not call A\* to move.**

📊 **Statistics & limitations**

The Record stats option saves the mode, score, and movement counters whenever fruit is eaten. The chart compares the average cumulative number of moves needed to reach a given score. Training games do not contribute to this chart.

The state provided to the network does not describe the snake’s entire body. The DQN can therefore still become trapped or take detours. Its performance depends on training and should be evaluated across multiple games.

💡 **Why this project matters**

This project combines heuristic search, reinforcement learning, Flask state management, Canvas rendering, and statistics. It offers a practical way to explore the difference between a strategy computed from explicit rules and a strategy learned from experiences and rewards.
