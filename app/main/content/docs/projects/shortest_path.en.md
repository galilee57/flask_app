---
title: Discover the shortest path
summary: English version
---

This project adapts chapter 2 of **L’intelligence artificielle en pratique avec Python**, by Hugues Bersini and Ken Hasselmann. Follow a path search through an undirected graph.

### How to use
Choose one of six book graphs (13, 15, 20, 40, 73 or 244 nodes), a start, a goal and an algorithm. **Run** animates the search; **Pause** suspends it; **Next step** expands one node. **Restart** resets the search. Changing a selection prepares a new search. The interval controls animation speed. Hiding the tab or opening this information panel pauses playback.

### A\* and Dijkstra
An edge costs the Euclidean distance between its endpoints. **g** is distance travelled; **h** estimates the remaining straight-line distance; **f = g + h** determines A\* priority. Dijkstra uses **h = 0**. Both find a minimum-cost path; A\* may explore fewer nodes. Ties may yield different equally optimal paths.

### Read the graph
The start is green, the goal coral, frontier nodes yellow and visited nodes blue. The current node has a white outline. The final path appears in white, alongside its cost and node sequence. Hover over an edge to read its distance. The 244-node graph hides permanent node labels for readability; the selectors still allow every node to be chosen.

Distances use file coordinates, not kilometres. Calculations retain full precision; displayed values are rounded to two decimal places. Identical start and goal nodes produce zero cost. Unreachable goals are explicitly reported.

### Sources and implementation
The six datasets come from [AI-book / Shortest_Path](https://github.com/iridia-ulb/AI-book/tree/main/Shortest_Path), © 2021 IRIDIA, ULB, under the MIT license included with the data. The Python engine and Flask / SVG interface are a new implementation **coded with Codex**. This version compares unidirectional A\* and Dijkstra; it does not implement the travelling salesman problem or bidirectional search. No results are saved and no external service is needed at runtime.
