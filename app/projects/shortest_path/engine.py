"""Deterministic shortest-path search on the book's undirected graphs."""
import heapq
import math
from functools import lru_cache
from pathlib import Path

DATASETS = (13, 15, 20, 40, 73, 244)


@lru_cache(maxsize=len(DATASETS))
def load_graph(size):
    if size not in DATASETS:
        raise ValueError("unknown_graph")
    lines = (Path(__file__).parent / "datasets" / f"{size}_nodes.txt").read_text().splitlines()
    count = int(lines[0])
    nodes = {int(i): (float(x), float(y)) for i, x, y in
             (line.split() for line in lines[1:count + 1])}
    # Keep full precision: Euclidean h must never exceed an edge's cost.
    edges = [(a, b, math.dist(nodes[a], nodes[b])) for a, b in
             (map(int, line.split()) for line in lines[count + 1:] if line.strip())]
    return nodes, edges


def search(nodes, edges, start, goal, algorithm="astar"):
    if start not in nodes or goal not in nodes:
        raise ValueError("unknown_node")
    if algorithm not in ("astar", "dijkstra"):
        raise ValueError("unknown_algorithm")
    neighbors = {node: [] for node in nodes}
    for a, b, weight in edges:
        neighbors[a].append((b, weight))
        neighbors[b].append((a, weight))
    def heuristic(node):
        return math.dist(nodes[node], nodes[goal]) if algorithm == "astar" else 0
    queue = [(heuristic(start), 0, start)]
    distances, parents, visited, steps = {start: 0}, {}, set(), []
    while queue:
        _, cost, node = heapq.heappop(queue)
        if node in visited or cost > distances[node]:
            continue
        visited.add(node)
        if node != goal:
            for other, weight in neighbors[node]:
                candidate = cost + weight
                if candidate < distances.get(other, math.inf):
                    distances[other], parents[other] = candidate, node
                    heapq.heappush(queue, (candidate + heuristic(other), candidate, other))
        frontier = sorted(set(distances) - visited)
        steps.append({"current": node, "visited": sorted(visited), "frontier": frontier,
                      "g": cost, "h": heuristic(node), "f": cost + heuristic(node)})
        if node == goal:
            path = [goal]
            while path[-1] != start:
                path.append(parents[path[-1]])
            return {"path": path[::-1], "cost": cost, "steps": steps, "visited": len(visited)}
    return {"path": [], "cost": None, "steps": steps, "visited": len(visited)}
