---
title: 🧩 Project – Tetris and Explainable Artificial Intelligence
summary: English Version
---

**This project revisits Tetris to show how an AI chooses its placements. Two modes are available: human control and heuristic AI. A neural network will be developed later.**

The goal is to complete horizontal lines using the seven piece types. Full lines disappear, freeing up space. The game ends when a new piece can no longer spawn.

🎮 **Gameplay & interface**

The 10-column × 20-row board is drawn on a JavaScript Canvas. Pieces are drawn from seven-piece bags: every type appears once before the bag is refilled. A preview shows the next piece, and a ghost shows where the current piece would land.

→ Left and right arrows move the piece; the up arrow rotates it clockwise.
→ The down arrow speeds up descent; Space drops the piece immediately.
→ Play starts the game, Pause suspends it, Resume continues it, and Restart resets the board. P also toggles pause.
→ Touch controls allow play without a keyboard. Changing mode starts a new game.
→ Hiding the tab or opening this information panel pauses a running game.

🧭 **AI mode: comparing placements**

The current AI uses explicit rules, with no learning or neural network. It simulates possible rotations and horizontal moves before descent, then evaluates each distinct placement. Metrics are calculated after clearing completed lines:

→ **Lines**: the number of lines completed by this piece.
→ **Total height**: the sum of the ten column heights.
→ **Holes**: empty cells beneath a block.
→ **Bumpiness**: the sum of height differences between neighbouring columns.

A placement’s value is **8 × lines − 0.5 × total height − 7 × holes − 0.3 × bumpiness**. A game over adds a **10,000** penalty. The AI chooses the highest value; ties keep the first placement explored. This evaluation value is separate from the game score.

🔎 **Watching decisions**

The panel shows the three best placements, their metrics, and their values. “Col.” indicates the leftmost occupied column, from 1 to 10; “↻” indicates the number of rotations. A dashed target marks the chosen placement on the board.

The AI allows reading time, performs its rotations and horizontal moves, then descends one cell at a time. **Advance manually** suspends automatic progress: each click on **Next step** displays a decision or performs one action, even while paused.

⏱️ **Independent speeds**

The human slider controls automatic descent from 800 to 80 milliseconds per cell. The AI slider controls actions from 2 to 0.2 seconds, with a default of 1.6 seconds. The decision and its outcome remain visible for three intervals. Both settings are kept separately during the page session.

📊 **Scores & records**

Clearing 1, 2, 3, or 4 lines awards **100, 300, 500, or 800 points**, respectively. Soft drops award 1 point per cell, and hard drops award 2 points per cell. The AI’s animated descent retains the same 2-point scoring rule. Speed does not multiply points.

Human and AI best scores are separate and stored in the browser. They are not sent to a server. If local storage is unavailable, the record is kept only for the page session.

🧠 **Limitations & future neural network**

The heuristic evaluates the current piece without planning a sequence of pieces. A locally favourable decision can therefore make later play harder. It does not search every possible move underneath blocks. Rotations use simple horizontal corrections, without a complete SRS system or lock delay.

The engine is independent of the interface. An agent interface is ready to accept a future neural network policy. Custom agents can have their actions animated, but no decision metric is presented as an explanation unless that agent provides it.

💡 **Why this project matters**

The project combines simulation, heuristic search, Canvas rendering, Tailwind CSS 4, and bilingual Flask content. Its educational goal is to make decisions observable and prepare a comparison between explicit rules and a learned strategy.
