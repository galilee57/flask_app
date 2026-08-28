import heapq

def get_neighbors(pos, grid_w, grid_h):
    x, y = pos

    candidates = [
        (x, y - 1),     # up
        (x, y + 1),     # down
        (x - 1, y),     # left
        (x + 1, y)      # right
    ]

    return [
        (nx, ny)
        for nx, ny in candidates
        if 0 <= nx < grid_w and 0 <= ny < grid_h
        ]

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(came_from, current):
    path = [current]

    while current in came_from:
        current = came_from[current]
        path.append(current)

    path.reverse()
    return path

def path_to_direction(path):
    if len(path) < 2:
        return None

    x1, y1 = path[0]
    x2, y2 = path[1]

    if x2 > x1:
        return "right"
    if x2 < x1:
        return "left"
    if y2 > y1:
        return "down"
    if y2 < y1:
        return "up"

    return None

def astar(start, goal, grid_w, grid_h, obstacles):
    obstacles = {(o["x"], o["y"]) for o in obstacles}

    start = (start["x"], start["y"])
    goal = (goal["x"], goal["y"])

    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(current, grid_w, grid_h):
            if neighbor in obstacles:
                continue

            tentative_g = g_score[current] + 1

            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))

    return []